from yardim_masasi.talepler import (
    ara,
    durum_sayilari,
    etiket_gruplari,
    kapanmamislar,
    oncelik_sirasi,
    ozet_satiri,
)

TALEPLER = [
    {"id": 4, "baslik": "Ödeme iki kez çekildi", "durum": "beklemede", "oncelik": "yuksek", "etiketler": ["odeme", "fatura"]},
    {"id": 1, "baslik": "Giriş yapamıyorum", "durum": "acik", "oncelik": "yuksek", "etiketler": ["hesap", "giris"]},
    {"id": 2, "baslik": "Fatura adresim yanlış görünüyor", "durum": "kapali", "oncelik": "orta", "etiketler": ["fatura"]},
    {"id": 7, "baslik": "Fatura gelmedi", "durum": "acik", "oncelik": "orta", "etiketler": ["fatura"]},
    {"id": 9, "baslik": "Karanlık mod isteği", "durum": "beklemede", "oncelik": "dusuk", "etiketler": []},
    {"id": 10, "baslik": "Giriş kodu SMS ile gelmiyor", "durum": "acik", "oncelik": "yuksek", "etiketler": ["hesap", "giris"]},
]


def idler(talepler):
    return [talep["id"] for talep in talepler]


def test_kapanmamislar_kapali_olanlari_atar_sirayi_korur():
    assert idler(kapanmamislar(TALEPLER)) == [4, 1, 7, 9, 10]


def test_durum_sayilari_her_durumu_sayar():
    assert durum_sayilari(TALEPLER) == {"acik": 3, "beklemede": 2, "kapali": 1}


def test_durum_sayilari_bos_listede_sifirlari_da_yazar():
    assert durum_sayilari([]) == {"acik": 0, "beklemede": 0, "kapali": 0}


def test_durum_sayilari_bilinmeyen_durumu_saymaz():
    talepler = TALEPLER + [{"id": 99, "baslik": "Deneme", "durum": "silindi", "oncelik": "orta", "etiketler": []}]
    assert durum_sayilari(talepler) == {"acik": 3, "beklemede": 2, "kapali": 1}


def test_etiket_gruplari_her_etiketin_taleplerini_listedeki_sirayla_verir():
    assert etiket_gruplari(TALEPLER) == {
        "fatura": [4, 2, 7],
        "giris": [1, 10],
        "hesap": [1, 10],
        "odeme": [4],
    }


def test_etiket_gruplari_anahtarlari_alfabetik_sirada():
    assert list(etiket_gruplari(TALEPLER)) == ["fatura", "giris", "hesap", "odeme"]


def test_oncelik_sirasi_once_oncelik_sonra_numara():
    assert idler(oncelik_sirasi(TALEPLER)) == [1, 4, 10, 2, 7, 9]


def test_oncelik_sirasi_verilen_listeyi_degistirmez():
    oncelik_sirasi(TALEPLER)
    assert idler(TALEPLER) == [4, 1, 2, 7, 9, 10]


def test_ara_basliklarda_buyuk_kucuk_harf_ayirmadan_arar():
    assert ara(TALEPLER, "fatura") == [2, 7]
    assert ara(TALEPLER, "GİRİŞ") == [1, 10]
    assert ara(TALEPLER, "ÖDEME") == [4]

    iade = {"id": 6, "baslik": "İade talebimin durumu", "durum": "beklemede", "oncelik": "orta", "etiketler": ["odeme"]}
    assert ara([iade], "iade") == [6]


def test_ara_butun_kelimeler_gecmeli():
    assert ara(TALEPLER, "giriş", "sms") == [10]
    assert ara(TALEPLER, "giriş", "fatura") == []


def test_ara_durum_yalniz_adiyla_verilir():
    assert ara(TALEPLER, "fatura", durum="acik") == [7]
    assert ara(TALEPLER, durum="beklemede") == [4, 9]
    assert ara(TALEPLER) == [4, 1, 2, 7, 9, 10]


def test_ozet_satiri_hizali_yazar():
    assert ozet_satiri(TALEPLER[3]) == "#  7 orta   acik      Fatura gelmedi"
    assert ozet_satiri(TALEPLER[0]) == "#  4 yuksek beklemede Ödeme iki kez çekildi"


def test_ozet_satiri_uzun_basligi_kisaltir():
    talep = {"id": 112, "baslik": "Aboneliğimi iptal etmek istiyorum", "durum": "acik", "oncelik": "dusuk", "etiketler": []}
    assert ozet_satiri(talep) == "#112 dusuk  acik      Aboneliğimi iptal etmek istiy…"
