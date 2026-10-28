import json
from pathlib import Path

import pytest

from yardim_masasi.model import (
    Durum,
    GecersizTalep,
    Oncelik,
    Talep,
    TalepDosyasiHatasi,
    talepleri_oku,
)

ORNEK = Path(__file__).parent.parent / "ornek" / "talepler.json"


def gecerli(**degisiklik):
    veri = {
        "id": 7,
        "baslik": "Fatura gelmedi",
        "durum": "acik",
        "oncelik": "orta",
        "musteri": "elif@example.com",
        "etiketler": ["fatura"],
    }
    veri.update(degisiklik)
    return veri


def hata_mesaji(veri):
    with pytest.raises(GecersizTalep) as bilgi:
        Talep.sozlukten(veri)
    return str(bilgi.value)


def yaz(yol, icerik):
    yol.write_text(icerik, encoding="utf-8")
    return yol


def test_gecerli_sozluk_talebe_doner():
    talep = Talep.sozlukten(gecerli())
    assert talep == Talep(7, "Fatura gelmedi", Durum.ACIK, Oncelik.ORTA, "elif@example.com", ("fatura",))
    assert talep.durum is Durum.ACIK
    assert talep.oncelik is Oncelik.ORTA


def test_etiketler_yoksa_bos_tuple():
    veri = gecerli()
    del veri["etiketler"]
    assert Talep.sozlukten(veri).etiketler == ()


def test_fazla_alanlar_yok_sayilir():
    assert Talep.sozlukten(gecerli(kanal="eposta")) == Talep.sozlukten(gecerli())


def test_sozluk_olmayan_veri():
    assert hata_mesaji(["acik"]) == "talep bir JSON nesnesi olmalı"


def test_ilk_eksik_alan_yazilir():
    assert hata_mesaji({}) == "eksik alan: id"
    assert hata_mesaji({"id": 7}) == "eksik alan: baslik"
    assert hata_mesaji({"id": 7, "baslik": "x"}) == "eksik alan: durum"
    assert hata_mesaji({"id": 7, "baslik": "x", "durum": "acik", "oncelik": "orta"}) == "eksik alan: musteri"


def test_gecersiz_id():
    assert hata_mesaji(gecerli(id="7")) == "geçersiz id: '7'"
    assert hata_mesaji(gecerli(id=0)) == "geçersiz id: 0"
    assert hata_mesaji(gecerli(id=-3)) == "geçersiz id: -3"


def test_bos_baslik():
    assert hata_mesaji(gecerli(baslik="   ")) == "başlık boş olamaz"
    assert hata_mesaji(gecerli(baslik=None)) == "başlık boş olamaz"


def test_bilinmeyen_durum_ve_nedeni():
    with pytest.raises(GecersizTalep) as bilgi:
        Talep.sozlukten(gecerli(durum="silindi"))
    assert str(bilgi.value) == "bilinmeyen durum: 'silindi'"
    assert isinstance(bilgi.value.__cause__, ValueError)


def test_bilinmeyen_oncelik_ve_nedeni():
    with pytest.raises(GecersizTalep) as bilgi:
        Talep.sozlukten(gecerli(oncelik="acil"))
    assert str(bilgi.value) == "bilinmeyen öncelik: 'acil'"
    assert isinstance(bilgi.value.__cause__, ValueError)


def test_gecersiz_musteri():
    assert hata_mesaji(gecerli(musteri="elif")) == "geçersiz müşteri: 'elif'"
    assert hata_mesaji(gecerli(musteri=None)) == "geçersiz müşteri: None"


def test_etiketler_metin_listesi_olmali():
    assert hata_mesaji(gecerli(etiketler="fatura")) == "etiketler bir metin listesi olmalı"
    assert hata_mesaji(gecerli(etiketler=["fatura", 3])) == "etiketler bir metin listesi olmalı"


def test_ornek_dosya_okunur():
    talepler = talepleri_oku(ORNEK)
    assert len(talepler) == 12
    assert all(isinstance(talep, Talep) for talep in talepler)
    assert talepler[0].baslik == "Giriş yapamıyorum"
    assert talepler[8].etiketler == ()


def test_olmayan_dosya(tmp_path):
    yol = tmp_path / "yok.json"
    with pytest.raises(TalepDosyasiHatasi) as bilgi:
        talepleri_oku(yol)
    assert str(bilgi.value) == f"dosya bulunamadı: {yol}"
    assert isinstance(bilgi.value.__cause__, FileNotFoundError)


def test_klasor_okunamaz(tmp_path):
    with pytest.raises(TalepDosyasiHatasi) as bilgi:
        talepleri_oku(tmp_path)
    assert str(bilgi.value) == f"dosya okunamadı: {tmp_path}"
    assert isinstance(bilgi.value.__cause__, OSError)


def test_bozuk_json(tmp_path):
    yol = yaz(tmp_path / "bozuk.json", '[{"id": 1,}]\n')
    with pytest.raises(TalepDosyasiHatasi) as bilgi:
        talepleri_oku(yol)
    assert str(bilgi.value) == f"geçerli JSON değil: {yol} (satır 1, sütun 10)"
    assert isinstance(bilgi.value.__cause__, json.JSONDecodeError)


def test_liste_olmayan_json(tmp_path):
    yol = yaz(tmp_path / "nesne.json", json.dumps(gecerli()))
    with pytest.raises(TalepDosyasiHatasi) as bilgi:
        talepleri_oku(yol)
    assert str(bilgi.value) == f"talep listesi bekleniyordu: {yol}"


def test_gecersiz_talebin_sirasi_yazilir(tmp_path):
    yol = yaz(tmp_path / "talepler.json", json.dumps([gecerli(id=1), gecerli(id=2, oncelik="acil")]))
    with pytest.raises(GecersizTalep) as bilgi:
        talepleri_oku(yol)
    assert str(bilgi.value) == "2. talep: bilinmeyen öncelik: 'acil'"
    assert isinstance(bilgi.value.__cause__, GecersizTalep)


def test_tekrarlanan_id(tmp_path):
    yol = yaz(tmp_path / "talepler.json", json.dumps([gecerli(id=1), gecerli(id=2), gecerli(id=1)]))
    with pytest.raises(GecersizTalep) as bilgi:
        talepleri_oku(yol)
    assert str(bilgi.value) == "3. talep: tekrarlanan id: 1"
