import time

import pytest

from yardim_masasi.araclar import yeniden_dene


@pytest.fixture
def beklemeler(monkeypatch):
    kayit = []
    monkeypatch.setattr(time, "sleep", kayit.append)
    return kayit


def bozuk(hata_sayisi, hata: type[Exception] = ConnectionError):
    cagrilar = []

    def fonk(*args, **kwargs):
        cagrilar.append((args, kwargs))
        if len(cagrilar) <= hata_sayisi:
            raise hata(f"deneme {len(cagrilar)}")
        return "tamam"

    return fonk, cagrilar


def test_ilk_denemede_basarili(beklemeler):
    fonk, cagrilar = bozuk(0)
    sarili = yeniden_dene(kez=3, hatalar=(ConnectionError,))(fonk)
    assert sarili() == "tamam"
    assert len(cagrilar) == 1
    assert beklemeler == []


def test_iki_hatadan_sonra_basarili(beklemeler):
    fonk, cagrilar = bozuk(2)
    sarili = yeniden_dene(kez=3, hatalar=(ConnectionError,), bekleme=0.5)(fonk)
    assert sarili() == "tamam"
    assert len(cagrilar) == 3
    assert beklemeler == [0.5, 0.5]


def test_haklar_bitince_son_hata_yukselir(beklemeler):
    fonk, cagrilar = bozuk(5)
    sarili = yeniden_dene(kez=3, hatalar=(ConnectionError,), bekleme=1)(fonk)
    with pytest.raises(ConnectionError, match="deneme 3"):
        sarili()
    assert len(cagrilar) == 3
    assert beklemeler == [1, 1]


def test_listede_olmayan_hata_hemen_yukselir(beklemeler):
    fonk, cagrilar = bozuk(1, hata=KeyError)
    sarili = yeniden_dene(kez=3, hatalar=(ConnectionError,))(fonk)
    with pytest.raises(KeyError):
        sarili()
    assert len(cagrilar) == 1
    assert beklemeler == []


def test_alt_sinif_da_yeniden_denenir(beklemeler):
    fonk, cagrilar = bozuk(1, hata=ConnectionRefusedError)
    sarili = yeniden_dene(kez=2, hatalar=(ConnectionError,))(fonk)
    assert sarili() == "tamam"
    assert len(cagrilar) == 2


def test_argumanlar_her_denemede_aynen_gecer(beklemeler):
    fonk, cagrilar = bozuk(1)
    sarili = yeniden_dene(kez=2, hatalar=(ConnectionError,))(fonk)
    sarili(1, 2, ad="httpx")
    assert cagrilar == [((1, 2), {"ad": "httpx"}), ((1, 2), {"ad": "httpx"})]


def test_tek_hak_yeniden_denemez(beklemeler):
    fonk, cagrilar = bozuk(1)
    sarili = yeniden_dene(kez=1, hatalar=(ConnectionError,))(fonk)
    with pytest.raises(ConnectionError):
        sarili()
    assert len(cagrilar) == 1
    assert beklemeler == []


def test_varsayilanlar(beklemeler):
    fonk, cagrilar = bozuk(5, hata=ValueError)
    with pytest.raises(ValueError):
        yeniden_dene()(fonk)()
    assert len(cagrilar) == 3
    assert beklemeler == [0.0, 0.0]


def test_gecersiz_hak_hemen_reddedilir():
    with pytest.raises(ValueError, match="kez en az 1 olmalı"):
        yeniden_dene(kez=0)


def test_ad_ve_belge_korunur():
    @yeniden_dene()
    def paket_getir():
        """Paketi getirir."""

    assert paket_getir.__name__ == "paket_getir"
    assert paket_getir.__doc__ == "Paketi getirir."


def test_dekorator_sozdizimiyle(beklemeler):
    sayac = 0

    @yeniden_dene(kez=4, hatalar=(TimeoutError,), bekleme=0.1)
    def islem(sayi):
        nonlocal sayac
        sayac += 1
        if sayac < 3:
            raise TimeoutError
        return sayi * 2

    assert islem(21) == 42
    assert sayac == 3
    assert beklemeler == [0.1, 0.1]
