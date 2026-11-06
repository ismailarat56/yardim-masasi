import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from yardim_masasi.model import Durum
from yardim_masasi.talepler import arguman_ayristirici, main


def test_bayraksiz_varsayilanlar():
    args = arguman_ayristirici().parse_args([])
    assert args.durum is None
    assert args.son_gun is None
    assert args.ayrintili is False


def test_bilinmeyen_bayrak_kullanim_hatasi(capsys):
    with pytest.raises(SystemExit) as cikis:
        main(["--renk", "mavi"])
    assert cikis.value.code == 2
    assert "--renk" in capsys.readouterr().err


def test_help_kod_0_ile_yardim_yazar(capsys):
    with pytest.raises(SystemExit) as cikis:
        main(["--help"])
    yakalanan = capsys.readouterr()

    assert cikis.value.code == 0
    assert "talep-ozeti" in yakalanan.out
    assert "--son-gun" in yakalanan.out
    assert yakalanan.err == ""


def test_version_kod_0_ile_surum_yazar(capsys):
    with pytest.raises(SystemExit) as cikis:
        main(["--version"])
    yakalanan = capsys.readouterr()

    assert cikis.value.code == 0
    assert yakalanan.out.startswith("talep-ozeti ")
    assert yakalanan.err == ""


def test_durum_kapali_enum_olarak_gelir():
    args = arguman_ayristirici().parse_args(["--durum", "kapali"])

    assert args.durum is Durum.KAPALI


def test_bilinmeyen_durum_kod_2_ile_cikar(capsys):
    with pytest.raises(SystemExit) as cikis:
        arguman_ayristirici().parse_args(["--durum", "bitti"])
    yakalanan = capsys.readouterr()

    assert cikis.value.code == 2
    assert "--durum" in yakalanan.err
    assert "bitti" in yakalanan.err
    assert yakalanan.out == ""


@pytest.mark.parametrize("deger", ["0", "-3", "abc"])
def test_gecersiz_son_gun_kod_2_ile_cikar(deger, capsys):
    with pytest.raises(SystemExit) as cikis:
        arguman_ayristirici().parse_args(["--son-gun", deger])
    yakalanan = capsys.readouterr()

    assert cikis.value.code == 2
    assert "--son-gun" in yakalanan.err
    assert deger in yakalanan.err
    assert yakalanan.out == ""


def test_son_gun_tam_sayi_olarak_gelir():
    args = arguman_ayristirici().parse_args(["--son-gun", "7"])

    assert args.son_gun == 7
    assert isinstance(args.son_gun, int)


def test_dosya_verilmezse_varsayilan_yol_gelir():
    args = arguman_ayristirici().parse_args([])

    assert args.dosya == Path("ornek/talepler.json")


def talep_verisi(numara, baslik, **ek):
    return {
        "id": numara,
        "baslik": baslik,
        "durum": "acik",
        "oncelik": "orta",
        "musteri": "ada@example.com",
        "etiketler": [],
        **ek,
    }


def jsonl_yaz(tmp_path, talepler):
    dosya = tmp_path / "talepler.jsonl"
    satirlar = [json.dumps(talep, ensure_ascii=False) for talep in talepler]
    dosya.write_text("\n".join(satirlar) + "\n", encoding="utf-8")
    return dosya


def test_etiket_yalniz_mobil_talebi_gosterir(tmp_path, capsys):
    dosya = jsonl_yaz(tmp_path, [
        talep_verisi(1, "Mobil giriş sorunu", etiketler=["mobil"]),
        talep_verisi(2, "Web giriş sorunu", etiketler=["web"]),
    ])

    kod = main([str(dosya), "--etiket", "mobil"])
    yakalanan = capsys.readouterr()

    assert kod == 0
    assert "Mobil giriş sorunu" in yakalanan.out
    assert "Web giriş sorunu" not in yakalanan.out
    assert "acik: 1, beklemede: 0, kapali: 0" in yakalanan.out
    assert yakalanan.err == ""


def test_olmayan_dosya_kod_1_ve_hata_mesaji_dondurur(tmp_path, capsys):
    dosya = tmp_path / "yok.jsonl"

    kod = main([str(dosya)])
    yakalanan = capsys.readouterr()

    assert kod == 1
    assert yakalanan.err.startswith("talep-ozeti:")
    assert str(dosya) in yakalanan.err
    assert yakalanan.out == ""


def test_son_yedi_gun_yalniz_dunku_talebi_gosterir(tmp_path, capsys):
    simdi = datetime.now(UTC)
    dosya = jsonl_yaz(tmp_path, [
        talep_verisi(1, "Dünkü talep", acildi=(simdi - timedelta(days=1)).isoformat()),
        talep_verisi(2, "Otuz günlük talep", acildi=(simdi - timedelta(days=30)).isoformat()),
    ])

    kod = main([str(dosya), "--son-gun", "7"])
    yakalanan = capsys.readouterr()

    assert kod == 0
    assert "Dünkü talep" in yakalanan.out
    assert "Otuz günlük talep" not in yakalanan.out
    assert "acik: 1, beklemede: 0, kapali: 0" in yakalanan.out
    assert yakalanan.err == ""
