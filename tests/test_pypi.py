import time

import httpx
import pytest

from yardim_masasi.pypi import ozet, paket_bilgisi, zaman_asimi


def test_ozet_ad_surum_ve_python_yazar():
    veri = {"info": {"name": "httpx", "version": "0.28.1", "requires_python": ">=3.8"}}
    assert ozet(veri) == "httpx 0.28.1 (Python >=3.8)"


def test_python_yoksa_belirtilmemis_yazar():
    veri = {"info": {"name": "eski", "version": "1.0", "requires_python": None}}
    assert ozet(veri) == "eski 1.0 (Python belirtilmemiş)"


def test_python_bos_metinse_belirtilmemis_yazar():
    veri = {"info": {"name": "eski", "version": "1.0", "requires_python": ""}}
    assert ozet(veri) == "eski 1.0 (Python belirtilmemiş)"


def test_zaman_asimi_varsayilan_on_saniye(monkeypatch):
    monkeypatch.delenv("PYPI_ZAMAN_ASIMI", raising=False)
    assert zaman_asimi() == 10.0


def test_zaman_asimi_ortamdan_okunur(monkeypatch):
    monkeypatch.setenv("PYPI_ZAMAN_ASIMI", "2.5")
    assert zaman_asimi() == 2.5


@pytest.mark.parametrize("hata_turu", [httpx.ConnectError, httpx.ReadTimeout])
def test_paket_bilgisi_gecici_hatadan_sonra_basarili(monkeypatch, hata_turu):
    cagrilar = []
    beklemeler = []
    veri = {"info": {"name": "httpx", "version": "0.28.1"}}

    def getir(url, *, timeout):
        cagrilar.append((url, timeout))
        istek = httpx.Request("GET", url)
        if len(cagrilar) < 3:
            raise hata_turu("geçici ağ hatası", request=istek)
        return httpx.Response(200, json=veri, request=istek)

    monkeypatch.setenv("PYPI_ZAMAN_ASIMI", "2.5")
    monkeypatch.setattr(httpx, "get", getir)
    monkeypatch.setattr(time, "sleep", beklemeler.append)

    assert paket_bilgisi("httpx") == veri
    assert cagrilar == [("https://pypi.org/pypi/httpx/json", 2.5)] * 3
    assert beklemeler == [0.5, 0.5]


def test_paket_bilgisi_son_ag_hatasini_aynen_yukseltir(monkeypatch):
    hatalar = []
    beklemeler = []

    def getir(url, *, timeout):
        hata = httpx.ConnectError("bağlantı kurulamadı", request=httpx.Request("GET", url))
        hatalar.append(hata)
        raise hata

    monkeypatch.setattr(httpx, "get", getir)
    monkeypatch.setattr(time, "sleep", beklemeler.append)

    with pytest.raises(httpx.ConnectError) as bilgi:
        paket_bilgisi("httpx")
    assert len(hatalar) == 3
    assert bilgi.value is hatalar[-1]
    assert beklemeler == [0.5, 0.5]


def test_paket_bilgisi_404_yeniden_denenmez(monkeypatch):
    cagrilar = []
    beklemeler = []

    def getir(url, *, timeout):
        cagrilar.append(url)
        return httpx.Response(404, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx, "get", getir)
    monkeypatch.setattr(time, "sleep", beklemeler.append)

    with pytest.raises(httpx.HTTPStatusError) as bilgi:
        paket_bilgisi("olmayan-paket")
    assert bilgi.value.response.status_code == 404
    assert len(cagrilar) == 1
    assert beklemeler == []


def sahte_pypi(monkeypatch, *yanitlar):
    """httpx.get yerine sırayla verilen yanıtları döndüren ya da hataları fırlatan bir fonksiyon koyar."""
    adresler = []

    def sahte_get(adres, timeout):
        adresler.append(adres)
        yanit = yanitlar[len(adresler) - 1]
        if isinstance(yanit, Exception):
            raise yanit
        return httpx.Response(yanit, json={"info": {"name": "httpx"}}, request=httpx.Request("GET", adres))

    monkeypatch.setattr(httpx, "get", sahte_get)
    monkeypatch.setattr(time, "sleep", lambda saniye: None)
    return adresler


def test_baglanti_hatasi_yeniden_denenir(monkeypatch):
    adresler = sahte_pypi(monkeypatch, httpx.ConnectError("bağlanamadı"), httpx.ReadTimeout("zaman aşımı"), 200)
    assert paket_bilgisi("httpx") == {"info": {"name": "httpx"}}
    assert len(adresler) == 3


def test_bulunamayan_paket_yeniden_denenmez(monkeypatch):
    adresler = sahte_pypi(monkeypatch, 404, 200)
    with pytest.raises(httpx.HTTPStatusError):
        paket_bilgisi("bu-paket-yok")
    assert len(adresler) == 1
