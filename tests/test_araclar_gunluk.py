import logging

import pytest

from yardim_masasi.araclar import yeniden_dene

KAYITCI = "yardim_masasi.araclar"


@pytest.fixture
def uyumadan(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda saniye: None)


def bozulan(kac_kez):
    cagri = {"sayi": 0}

    @yeniden_dene(kez=3, hatalar=(ConnectionError,), bekleme=0.5)
    def getir():
        cagri["sayi"] += 1
        if cagri["sayi"] <= kac_kez:
            raise ConnectionError("bağlantı koptu")
        return "tamam"

    return getir


def test_her_basarisiz_deneme_uyari_yazar(uyumadan, caplog):
    caplog.set_level(logging.WARNING, logger=KAYITCI)
    assert bozulan(2)() == "tamam"
    uyarilar = [k for k in caplog.records if k.levelno == logging.WARNING]
    assert len(uyarilar) == 2
    assert "1/3" in uyarilar[0].getMessage()
    assert "2/3" in uyarilar[1].getMessage()
    assert all(k.name == KAYITCI for k in uyarilar)


def test_son_deneme_de_bozulursa_hata_kaydi(uyumadan, caplog):
    caplog.set_level(logging.WARNING, logger=KAYITCI)
    with pytest.raises(ConnectionError):
        bozulan(5)()
    assert [k.levelname for k in caplog.records] == ["WARNING", "WARNING", "ERROR"]


def test_ilk_denemede_basarida_uyari_yok(uyumadan, caplog):
    caplog.set_level(logging.WARNING, logger=KAYITCI)
    assert bozulan(0)() == "tamam"
    assert caplog.records == []


def test_uyari_islem_hata_ve_bekleme_bilgilerini_icerir(uyumadan, caplog):
    caplog.set_level(logging.WARNING, logger=KAYITCI)
    assert bozulan(1)() == "tamam"
    assert caplog.records[0].getMessage() == (
        "getir: deneme 1/3 başarısız (ConnectionError), 0.5 sn sonra yeniden"
    )


def test_yeniden_denenmeyen_hata_kayit_yazmaz(uyumadan, caplog):
    caplog.set_level(logging.WARNING, logger=KAYITCI)

    @yeniden_dene(hatalar=(ConnectionError,))
    def getir():
        raise ValueError("geçersiz değer")

    with pytest.raises(ValueError, match="geçersiz değer"):
        getir()
    assert caplog.records == []
