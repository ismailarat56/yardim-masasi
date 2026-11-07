import json
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from importlib.metadata import version
from pathlib import Path

import pytest

from yardim_masasi.talepler import main

TALEP = {"id": 1, "baslik": "Giriş yapamıyorum", "durum": "acik", "oncelik": "yuksek", "musteri": "ayse@example.com"}


def calistir(monkeypatch, *argumanlar):
    monkeypatch.setattr("sys.argv", ["talep-ozeti", *argumanlar])
    return main()


def dosya(tmp_path, veri):
    yol = tmp_path / "talepler.json"
    yol.write_text(json.dumps(veri), encoding="utf-8")
    return yol


def test_gecerli_dosyanin_ozetini_yazar(tmp_path, monkeypatch, capsys):
    calistir(monkeypatch, str(dosya(tmp_path, [TALEP])))
    cikti = capsys.readouterr()
    assert cikti.out == "acik: 1, beklemede: 0, kapali: 0\n\n#  1 yuksek acik      Giriş yapamıyorum\n"
    assert cikti.err == ""


def test_olmayan_dosya_kod_1_ile_biter(tmp_path, monkeypatch, capsys):
    yol = tmp_path / "yok.json"
    assert calistir(monkeypatch, str(yol)) == 1
    cikti = capsys.readouterr()
    assert cikti.out == ""
    assert cikti.err == f"talep-ozeti: dosya bulunamadı: {yol}\n"


def test_gecersiz_talep_kod_1_ile_biter(tmp_path, monkeypatch, capsys):
    yol = dosya(tmp_path, [{**TALEP, "oncelik": "acil"}])
    assert calistir(monkeypatch, str(yol)) == 1
    assert capsys.readouterr().err == "talep-ozeti: 1. talep: bilinmeyen öncelik: 'acil'\n"


def test_fazla_arguman_kod_2_ile_biter(monkeypatch, capsys):
    with pytest.raises(SystemExit) as bilgi:
        calistir(monkeypatch, "a.json", "b.json")
    assert bilgi.value.code == 2
    cikti = capsys.readouterr()
    assert cikti.out == ""
    assert "usage: talep-ozeti" in cikti.err
    assert "unrecognized arguments: b.json" in cikti.err


def test_argv_dogrudan_verilir_ve_basari_kodu_doner(tmp_path, capsys):
    assert main([str(dosya(tmp_path, [TALEP]))]) == 0
    assert "acik: 1, beklemede: 0, kapali: 0" in capsys.readouterr().out


def test_kapali_filtresi_kapali_talepleri_listeler(tmp_path, capsys):
    yol = dosya(tmp_path, [TALEP, {**TALEP, "id": 2, "durum": "kapali"}])
    assert main([str(yol), "--durum", "kapali"]) == 0
    assert capsys.readouterr().out == (
        "acik: 0, beklemede: 0, kapali: 1\n\n"
        "#  2 yuksek kapali    Giriş yapamıyorum\n"
    )


def test_oncelik_etiket_birlikte_suzer_sayim_kapalilari_icerir(tmp_path, capsys):
    yol = dosya(tmp_path, [
        {**TALEP, "etiketler": ["mobil"]},
        {**TALEP, "id": 2, "durum": "kapali", "etiketler": ["mobil"]},
        {**TALEP, "id": 3, "oncelik": "dusuk", "etiketler": ["mobil"]},
        {**TALEP, "id": 4, "etiketler": ["web"]},
    ])
    assert main([str(yol), "--oncelik", "yuksek", "--etiket", "mobil"]) == 0
    assert capsys.readouterr().out == (
        "acik: 1, beklemede: 0, kapali: 1\n\n"
        "#  1 yuksek acik      Giriş yapamıyorum\n"
    )


def test_son_gun_jsonl_yeni_talebi_secer(tmp_path, capsys):
    simdi = datetime.now(UTC)
    yol = tmp_path / "zamanli.jsonl"
    veriler = [
        {**TALEP, "acildi": (simdi - timedelta(days=1)).isoformat()},
        {**TALEP, "id": 2, "acildi": (simdi - timedelta(days=30)).isoformat()},
        {**TALEP, "id": 3},
    ]
    yol.write_text("\n".join(json.dumps(t) for t in veriler), encoding="utf-8")
    assert main([str(yol), "--son-gun", "7"]) == 0
    assert capsys.readouterr().out == (
        "acik: 1, beklemede: 0, kapali: 0\n\n"
        "#  1 yuksek acik      Giriş yapamıyorum\n"
    )


@pytest.mark.parametrize("deger", ["abc", "-3", "0"])
def test_gecersiz_son_gun_kod_2_ile_biter(deger, capsys):
    with pytest.raises(SystemExit) as bilgi:
        main(["--son-gun", deger])
    assert bilgi.value.code == 2
    cikti = capsys.readouterr()
    assert cikti.out == ""
    assert "--son-gun" in cikti.err
    assert deger in cikti.err


@pytest.mark.parametrize("bayrak", ["--durum", "--oncelik"])
def test_gecersiz_enum_kod_2_ile_biter(bayrak, capsys):
    with pytest.raises(SystemExit) as bilgi:
        main([bayrak, "bitti"])
    assert bilgi.value.code == 2
    assert bayrak in capsys.readouterr().err


@pytest.mark.parametrize("bayrak", ["-v", "--ayrintili"])
def test_ayrintili_bayragi_kabul_edilir(tmp_path, capsys, bayrak):
    assert main([str(dosya(tmp_path, [TALEP])), bayrak]) == 0
    assert "acik: 1" in capsys.readouterr().out


def test_version_dosya_okumadan_surum_yazar(capsys):
    with pytest.raises(SystemExit) as bilgi:
        main(["yok.json", "--version"])
    assert bilgi.value.code == 0
    assert capsys.readouterr().out == f"talep-ozeti {version('yardim-masasi')}\n"


def test_modul_girisi_pypi_yardimini_gosterir():
    sonuc = subprocess.run(
        [sys.executable, "-m", "yardim_masasi", "--help"],
        capture_output=True, text=True, timeout=10,
    )
    assert sonuc.returncode == 0
    assert "usage: yardim-masasi" in sonuc.stdout
    assert "--eszamanli" in sonuc.stdout
    assert sonuc.stderr == ""


def test_talep_komutu_dosya_hatasinda_kod_1_dondurur(tmp_path):
    sonuc = subprocess.run(
        [str(Path(sys.executable).with_name("talep-ozeti")), str(tmp_path / "yok.json")],
        capture_output=True, text=True, timeout=10,
    )
    assert sonuc.returncode == 1
    assert "talep-ozeti: dosya bulunamadı:" in sonuc.stderr
    assert "Traceback" not in sonuc.stderr


def test_ayrintili_kayitlar_stderrde_stdout_ayni_kalir(tmp_path):
    yol = dosya(tmp_path, [TALEP, {**TALEP, "id": 2, "durum": "kapali"}])
    komut = [str(Path(sys.executable).with_name("talep-ozeti")), str(yol), "--durum", "kapali"]

    normal = subprocess.run(komut, capture_output=True, text=True, timeout=10)
    ayrintili = subprocess.run([*komut, "-v"], capture_output=True, text=True, timeout=10)

    assert normal.returncode == ayrintili.returncode == 0
    assert normal.stdout == ayrintili.stdout
    assert normal.stderr == ""
    assert ayrintili.stderr == (
        "DEBUG yardim_masasi.talepler: 2 talep okundu\n"
        "DEBUG yardim_masasi.talepler: Filtre sonrası 1 talep kaldı\n"
    )
