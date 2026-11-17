"""/saglik testleri: gerçek havuz yerine SahteHavuz. Veritabanı gerekmez."""

import pytest
from fastapi.testclient import TestClient
from psycopg import OperationalError
from psycopg_pool import PoolTimeout

from sahte_havuz import SahteHavuz
from yardim_masasi.api import app


@pytest.fixture
def istemci():
    return TestClient(app)


def havuz_koy(monkeypatch: pytest.MonkeyPatch, havuz: SahteHavuz) -> None:
    monkeypatch.setattr(app.state, "havuz", havuz, raising=False)


# /saglik: altına en az üç test yaz.


def test_saglik_veritabani_cevap_verince_200(istemci, monkeypatch):
    havuz = SahteHavuz()
    havuz_koy(monkeypatch, havuz)

    cevap = istemci.get("/saglik")

    assert cevap.status_code == 200
    assert cevap.json() == {"durum": "ok"}
    assert havuz.baglanti.sorgular == ["SELECT 1"]


def test_saglik_havuz_bekletirse_503(istemci, monkeypatch):
    havuz = SahteHavuz(bekleme_hatasi=PoolTimeout("havuz bağlantı veremedi"))
    havuz_koy(monkeypatch, havuz)

    cevap = istemci.get("/saglik")

    assert cevap.status_code == 503
    assert cevap.json() == {"durum": "veritabanına ulaşılamıyor"}
    assert havuz.baglanti.sorgular == []


def test_saglik_kopuk_baglantida_503(istemci, monkeypatch):
    havuz = SahteHavuz(sorgu_hatasi=OperationalError("bağlantı koptu"))
    havuz_koy(monkeypatch, havuz)

    cevap = istemci.get("/saglik")

    assert cevap.status_code == 503
    assert cevap.json() == {"durum": "veritabanına ulaşılamıyor"}
    assert havuz.baglanti.sorgular == ["SELECT 1"]


def test_saglik_en_cok_iki_saniye_bekler(istemci, monkeypatch):
    havuz = SahteHavuz()
    havuz_koy(monkeypatch, havuz)

    istemci.get("/saglik")

    assert havuz.istenen_sureler == [2]


def test_saglik_baska_hatayi_yutmaz(istemci, monkeypatch):
    havuz_koy(monkeypatch, SahteHavuz(sorgu_hatasi=RuntimeError("beklenmeyen hata")))

    with pytest.raises(RuntimeError):
        istemci.get("/saglik")
