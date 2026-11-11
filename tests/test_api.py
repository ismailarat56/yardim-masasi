"""API testleri veritabanı kullanmaz; lifespan çalıştırılmadan sahte depo kullanılır."""

import pytest
from fastapi.testclient import TestClient

from sahte_depo import BellekDeposu
from test_depo_sozlesme import ORNEKLER
from yardim_masasi.api import app, depo_al

ANAHTAR = "test-anahtari"


@pytest.fixture
def depo():
    return BellekDeposu(ORNEKLER)


@pytest.fixture
def istemci(depo, monkeypatch):
    monkeypatch.setenv("API_ANAHTARI", ANAHTAR)
    app.dependency_overrides[depo_al] = lambda: depo
    istemci = TestClient(app)
    try:
        yield istemci
    finally:
        istemci.close()
        app.dependency_overrides.clear()


def yetkili():
    return {"X-API-Anahtari": ANAHTAR}


def kosullu(etag):
    return {**yetkili(), "If-Match": etag}


def test_liste_hepsini_verir(istemci):
    yanit = istemci.get("/talepler")
    assert yanit.status_code == 200
    assert [talep["id"] for talep in yanit.json()] == [1, 2, 3, 4, 5]


def test_liste_duruma_gore(istemci):
    yanit = istemci.get("/talepler", params={"durum": "acik"})
    assert [talep["id"] for talep in yanit.json()] == [1, 3, 5]


def test_liste_bilinmeyen_durum_422(istemci):
    yanit = istemci.get("/talepler", params={"durum": "acil"})
    assert yanit.status_code == 422
    assert yanit.json()["detail"][0]["loc"] == ["query", "durum"]


def test_getir_alanlari_verir(istemci):
    yanit = istemci.get("/talepler/1")
    assert yanit.status_code == 200
    assert yanit.json() == {
        "id": 1, "baslik": "Giriş yapamıyorum", "durum": "acik", "oncelik": "yuksek",
        "musteri": "ayse@example.com", "etiketler": ["hesap", "giris"],
        "acildi": "2026-11-01T09:00:00Z",
        "surum": 1,
    }


def test_getir_olmayan_404(istemci):
    yanit = istemci.get("/talepler/99")
    assert yanit.status_code == 404
    assert yanit.json() == {"detail": "talep bulunamadı"}


@pytest.mark.parametrize("numara", ["0", "-3", "abc"])
def test_getir_gecersiz_numara_422(istemci, numara):
    assert istemci.get(f"/talepler/{numara}").status_code == 422


def test_ozet(istemci):
    yanit = istemci.get("/talepler/ozet")
    assert yanit.status_code == 200
    assert yanit.json() == {"acik": 3, "beklemede": 1, "kapali": 1}


def test_olustur_anahtarsiz_401(istemci):
    yanit = istemci.post("/talepler", json={"baslik": "Yeni talep", "musteri": "ali@example.com"})
    assert yanit.status_code == 401


def test_olustur_yanlis_anahtar_401(istemci):
    yanit = istemci.post(
        "/talepler", json={"baslik": "Yeni talep", "musteri": "ali@example.com"},
        headers={"X-API-Anahtari": "yanlis"},
    )
    assert yanit.status_code == 401


def test_olustur_201(istemci):
    yanit = istemci.post(
        "/talepler", json={"baslik": "Yeni talep", "musteri": "ali@example.com"}, headers=yetkili(),
    )
    assert yanit.status_code == 201
    govde = yanit.json()
    assert (govde["id"], govde["durum"], govde["oncelik"], govde["etiketler"]) == (6, "acik", "orta", [])


def test_olustur_istemci_durum_secemez(istemci):
    yanit = istemci.post(
        "/talepler", json={"baslik": "Yeni talep", "musteri": "ali@example.com", "durum": "kapali"},
        headers=yetkili(),
    )
    assert yanit.status_code == 422
    assert yanit.json()["detail"][0]["type"] == "extra_forbidden"


def test_olustur_kisa_baslik_422(istemci):
    yanit = istemci.post("/talepler", json={"baslik": " ab ", "musteri": "ali@example.com"}, headers=yetkili())
    assert yanit.status_code == 422
    assert yanit.json()["detail"][0]["type"] == "string_too_short"


def test_getir_etag_verir(istemci):
    yanit = istemci.get("/talepler/3")
    assert yanit.headers["ETag"] == '"1"'


def test_guncelle_200_ve_yeni_etag(istemci):
    yanit = istemci.patch("/talepler/4", json={"durum": "kapali"}, headers=kosullu('"1"'))
    assert yanit.status_code == 200
    assert (yanit.json()["durum"], yanit.json()["oncelik"], yanit.json()["surum"]) == ("kapali", "dusuk", 2)
    assert yanit.headers["ETag"] == '"2"'


def test_guncelle_bos_govde_422(istemci):
    yanit = istemci.patch("/talepler/4", json={}, headers=kosullu('"1"'))
    assert yanit.status_code == 422


def test_guncelle_olmayan_404(istemci):
    yanit = istemci.patch("/talepler/99", json={"durum": "kapali"}, headers=kosullu('"1"'))
    assert yanit.status_code == 404


def test_guncelle_if_match_yoksa_428(istemci):
    yanit = istemci.patch("/talepler/4", json={"durum": "kapali"}, headers=yetkili())
    assert yanit.status_code == 428
    assert istemci.get("/talepler/4").json()["durum"] == "beklemede"


def test_guncelle_anahtar_if_matchten_once_bakilir(istemci):
    yanit = istemci.patch("/talepler/4", json={"durum": "kapali"})
    assert yanit.status_code == 401


@pytest.mark.parametrize("deger", ["1", 'W/"1"', '"abc"', '"0"', "*"])
def test_guncelle_bicimsiz_if_match_400(istemci, deger):
    yanit = istemci.patch("/talepler/4", json={"durum": "kapali"}, headers=kosullu(deger))
    assert yanit.status_code == 400


def test_guncelle_eski_surum_412(istemci):
    istemci.patch("/talepler/4", json={"durum": "kapali"}, headers=kosullu('"1"'))
    yanit = istemci.patch("/talepler/4", json={"durum": "acik"}, headers=kosullu('"1"'))
    assert yanit.status_code == 412
    assert yanit.json() == {"detail": "talep sen okuduktan sonra değişti"}
    assert yanit.headers["ETag"] == '"2"'
    assert istemci.get("/talepler/4").json()["durum"] == "kapali"


# Ek testler: her biri geçici üretim kodu değişikliğiyle kırmızı görüldü.


def test_liste_etikete_gore(istemci):
    yanit = istemci.get("/talepler", params={"etiket": "hesap"})
    assert yanit.status_code == 200
    assert [talep["id"] for talep in yanit.json()] == [1, 3]


def test_olustur_baslik_ve_etiket_bosluklarini_temizler(istemci):
    yanit = istemci.post(
        "/talepler", headers=yetkili(),
        json={"baslik": "  Yeni talep  ", "musteri": "ali@example.com", "etiketler": [" hesap ", " giris "]},
    )
    assert yanit.status_code == 201
    assert yanit.json()["baslik"] == "Yeni talep"
    assert yanit.json()["etiketler"] == ["hesap", "giris"]


def test_olustur_gecersiz_musteri_422(istemci):
    yanit = istemci.post(
        "/talepler", json={"baslik": "Yeni talep", "musteri": "gecersiz"}, headers=yetkili(),
    )
    assert yanit.status_code == 422
    assert yanit.json()["detail"][0]["loc"] == ["body", "musteri"]


def test_guncelle_anahtarsiz_401(istemci):
    yanit = istemci.patch("/talepler/4", json={"durum": "kapali"})
    assert yanit.status_code == 401
    assert istemci.get("/talepler/4").json()["durum"] == "beklemede"


def test_olusturulan_talep_get_ile_aynen_okunur(istemci):
    olusan = istemci.post(
        "/talepler", headers=yetkili(),
        json={"baslik": "Yeni talep", "musteri": "ali@example.com", "oncelik": "yuksek", "etiketler": ["yeni"]},
    )
    assert olusan.status_code == 201
    yanit = istemci.get(f"/talepler/{olusan.json()['id']}")
    assert yanit.status_code == 200
    assert yanit.json() == olusan.json()


def test_anahtar_tanimli_degilse_yazma_kapali(istemci, monkeypatch):
    monkeypatch.delenv("API_ANAHTARI")
    yanit = istemci.post(
        "/talepler", json={"baslik": "Yeni talep", "musteri": "ali@example.com"}, headers=yetkili(),
    )
    assert yanit.status_code == 401
    assert len(istemci.get("/talepler").json()) == 5


def test_ascii_olmayan_anahtar_401(istemci):
    yanit = istemci.post(
        "/talepler", json={"baslik": "Yeni talep", "musteri": "ali@example.com"},
        headers={"X-API-Anahtari": "şifre".encode()},
    )
    assert yanit.status_code == 401
