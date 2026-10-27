from yardim_masasi.metin import (
    bosluklari_duzelt,
    buyuk_harf,
    etiketleri_ayir,
    kisalt,
    kucuk_harf,
    maskele,
)


def test_kucuk_harf_turkce_i_harflerini_dogru_cevirir():
    assert kucuk_harf("İSTANBUL") == "istanbul"
    assert kucuk_harf("IŞIK") == "ışık"
    assert kucuk_harf("ÇAĞRI ÖZ") == "çağrı öz"


def test_kucuk_harf_harf_sayisini_degistirmez():
    assert kucuk_harf("İsmail") == "ismail"
    assert len(kucuk_harf("İsmail")) == 6


def test_buyuk_harf_turkce_i_harflerini_dogru_cevirir():
    assert buyuk_harf("istanbul") == "İSTANBUL"
    assert buyuk_harf("ılık su") == "ILIK SU"
    assert buyuk_harf("çiğdem") == "ÇİĞDEM"


def test_bosluklari_duzelt_bastaki_sondaki_ve_aradaki_bosluklari_teke_indirir():
    assert bosluklari_duzelt("  Giriş \t yapamıyorum\n ") == "Giriş yapamıyorum"
    assert bosluklari_duzelt("Fatura") == "Fatura"
    assert bosluklari_duzelt("   ") == ""


def test_etiketleri_ayir_temizler_kucultur_ve_tekrari_atar():
    metin = "Hesap, GİRİŞ ,, hesap , Ödeme   Sorunu"
    assert etiketleri_ayir(metin) == ["hesap", "giriş", "ödeme sorunu"]


def test_etiketleri_ayir_ilk_gorulen_sirayi_korur():
    metin = "odeme, hesap, fatura, giris, odeme, uygulama"
    assert etiketleri_ayir(metin) == ["odeme", "hesap", "fatura", "giris", "uygulama"]


def test_etiketleri_ayir_bos_metinde_bos_liste_doner():
    assert etiketleri_ayir("") == []
    assert etiketleri_ayir(" ,  , ") == []


def test_kisalt_sigan_metne_dokunmaz():
    assert kisalt("Fatura gelmedi") == "Fatura gelmedi"
    assert kisalt("Fatura gelmedi", 14) == "Fatura gelmedi"


def test_kisalt_uzun_metni_uc_nokta_ile_bitirir():
    assert kisalt("Fatura gelmedi", 13) == "Fatura gelme…"
    assert kisalt("Şifre sıfırlama e-postası gelmiyor") == "Şifre sıfırlama e-postası gel…"


def test_kisalt_kesilen_yerdeki_boslugu_atar():
    assert kisalt("Fatura gelmedi", 8) == "Fatura…"


def test_kisalt_sonucu_hicbir_zaman_sinirdan_uzun_degil():
    metin = "Aboneliğimi iptal etmek istiyorum"
    for en_fazla in range(2, 40):
        assert len(kisalt(metin, en_fazla)) <= en_fazla


def test_maskele_adin_ilk_harfini_ve_alan_adini_birakir():
    assert maskele("ayse@example.com") == "a***@example.com"
    assert maskele("a@example.com") == "a***@example.com"


def test_maskele_gecersiz_adreste_yalniz_yildiz_doner():
    assert maskele("gecersiz") == "***"
    assert maskele("@example.com") == "***"
    assert maskele("ayse@") == "***"
