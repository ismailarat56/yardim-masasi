"""PgTalepDeposu ve BellekDeposu aynı sözleşmeye uyar: aynı testler ikisinde de koşar.

PostgreSQL testleri TEST_DATABASE_URL tanımlı değilse atlanır:
    uv run --env-file .env pytest tests/test_depo_sozlesme.py
"""

import asyncio
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta

import psycopg
import pytest
from psycopg_pool import AsyncConnectionPool

from sahte_depo import BellekDeposu
from yardim_masasi.model import Durum, Oncelik, SurumCakismasi, Talep
from yardim_masasi.pg_depo import PgTalepDeposu
from yardim_masasi.sayfa import Ayrac
from yardim_masasi.veritabani import ornekleri_yukle

pytestmark = pytest.mark.anyio

T0 = datetime(2026, 11, 1, 9, 0, tzinfo=UTC)

ORNEKLER = [
    Talep(1, "Giriş yapamıyorum", Durum.ACIK, Oncelik.YUKSEK, "ayse@example.com", ("hesap", "giris"), T0),
    Talep(2, "Fatura adresi yanlış", Durum.KAPALI, Oncelik.ORTA, "mehmet@example.com", ("fatura",), T0 + timedelta(hours=1)),
    Talep(3, "Şifre e-postası gelmiyor", Durum.ACIK, Oncelik.YUKSEK, "zeynep@example.com", ("hesap",), T0 + timedelta(hours=2)),
    Talep(4, "Uygulama açılışta donuyor", Durum.BEKLEMEDE, Oncelik.DUSUK, "can@example.com", ("mobil",), T0 + timedelta(hours=3)),
    Talep(5, "Kargo takip numarası yok", Durum.ACIK, Oncelik.ORTA, "ela@example.com", (), T0 + timedelta(hours=4)),
]


# Açılış zamanları numara sırasıyla gitmiyor; bazı talepler aynı anda açılmış.
KARISIK = [
    Talep(1, "Kargo gecikti", Durum.ACIK, Oncelik.ORTA, "a@example.com", (), T0 + timedelta(hours=2)),
    Talep(2, "Fatura gelmedi", Durum.ACIK, Oncelik.ORTA, "b@example.com", (), T0),
    Talep(3, "Şifre sıfırlanmıyor", Durum.ACIK, Oncelik.ORTA, "c@example.com", (), T0 + timedelta(hours=2)),
    Talep(4, "İade yatmadı", Durum.ACIK, Oncelik.ORTA, "d@example.com", (), T0),
    Talep(5, "Hesap kilitlendi", Durum.ACIK, Oncelik.ORTA, "e@example.com", (), T0 + timedelta(hours=1)),
    Talep(6, "Uygulama donuyor", Durum.ACIK, Oncelik.ORTA, "f@example.com", (), T0 + timedelta(hours=2)),
]


@asynccontextmanager
async def depo_ac(request, tur, talepler):
    if tur == "bellek":
        yield BellekDeposu(talepler)
        return
    adres = request.getfixturevalue("test_adresi")
    with psycopg.connect(adres) as baglanti:
        baglanti.execute("TRUNCATE talepler RESTART IDENTITY CASCADE")
        ornekleri_yukle(baglanti, talepler)
    havuz = AsyncConnectionPool(adres, connection_class=psycopg.AsyncConnection, min_size=1, max_size=2, open=False)
    await havuz.open(wait=True, timeout=5)
    try:
        yield PgTalepDeposu(havuz)
    finally:
        await havuz.close()


@pytest.fixture(params=["bellek", "pg"])
async def depo(request):
    async with depo_ac(request, request.param, ORNEKLER) as acilan:
        yield acilan


@pytest.fixture(params=["bellek", "pg"])
async def karisik_depo(request):
    async with depo_ac(request, request.param, KARISIK) as acilan:
        yield acilan


def numaralar(sayfa):
    return [talep.id for talep in sayfa.talepler]


async def butun_sayfalar(depo, **secenekler):
    """Sonraki ayracı izleyerek bütün sayfaları okur; numaraları sırayla döndürür."""
    gorulen = []
    sonra = None
    for _ in range(100):
        sayfa = await depo.listele(sonra=sonra, **secenekler)
        gorulen += numaralar(sayfa)
        if sayfa.sonraki is None:
            return gorulen
        sonra = sayfa.sonraki
    raise AssertionError(f"100 sayfada bitmedi: {gorulen[:20]}")


# getir, ekle, durum_sayilari (hazır verildi)


async def test_getir_talebi_bulur(depo):
    talep = await depo.getir(1)
    assert talep == ORNEKLER[0]


async def test_getir_olmayan_talepte_none(depo):
    assert await depo.getir(99) is None


async def test_ekle_yeni_numara_en_buyukten_sonra_gelir(depo):
    talep = await depo.ekle(baslik="Yeni talep", musteri="ali@example.com", oncelik=Oncelik.DUSUK, etiketler=["yeni"])
    assert talep.id == 6
    assert talep.durum == Durum.ACIK
    assert talep.etiketler == ("yeni",)
    assert talep.acildi is not None
    assert await depo.getir(6) == talep


async def test_durum_sayilari(depo):
    assert await depo.durum_sayilari() == {Durum.ACIK: 3, Durum.BEKLEMEDE: 1, Durum.KAPALI: 1}


# listele: en yeniden eskiye, sayfa sayfa (senin yazdığın)


async def test_listele_en_yeniden_eskiye(depo):
    sayfa = await depo.listele()
    assert numaralar(sayfa) == [5, 4, 3, 2, 1]
    assert sayfa.sonraki is None


async def test_listele_sira_numaraya_degil_zamana_gore(karisik_depo):
    assert numaralar(await karisik_depo.listele()) == [6, 3, 1, 5, 4, 2]


async def test_listele_varsayilan_limit_yirmi(depo):
    for sira in range(20):
        await depo.ekle(baslik=f"Yeni talep {sira}", musteri="ali@example.com", oncelik=Oncelik.ORTA, etiketler=[])
    sayfa = await depo.listele()
    assert len(sayfa.talepler) == 20
    assert sayfa.sonraki is not None
    buyuk = await depo.listele(limit=24)
    assert len(buyuk.talepler) == 24
    assert buyuk.sonraki is not None


async def test_listele_limit_kadar_verir_ve_ayrac_birakir(depo):
    sayfa = await depo.listele(limit=2)
    assert numaralar(sayfa) == [5, 4]
    assert sayfa.sonraki == Ayrac.talepten(ORNEKLER[3])


async def test_listele_ayractan_sonrasini_verir(depo):
    sayfa = await depo.listele(limit=2, sonra=Ayrac.talepten(ORNEKLER[3]))
    assert numaralar(sayfa) == [3, 2]
    assert sayfa.sonraki == Ayrac.talepten(ORNEKLER[1])


async def test_listele_son_sayfada_ayrac_yok(depo):
    sayfa = await depo.listele(limit=2, sonra=Ayrac.talepten(ORNEKLER[1]))
    assert numaralar(sayfa) == [1]
    assert sayfa.sonraki is None


async def test_listele_tam_dolan_son_sayfada_ayrac_yok(depo):
    sayfa = await depo.listele(limit=5)
    assert numaralar(sayfa) == [5, 4, 3, 2, 1]
    assert sayfa.sonraki is None


async def test_listele_en_eskiden_sonrasi_bos(depo):
    sayfa = await depo.listele(sonra=Ayrac.talepten(ORNEKLER[0]))
    assert sayfa.talepler == []
    assert sayfa.sonraki is None


@pytest.mark.parametrize("limit", [1, 2, 3, 4, 5, 6])
async def test_sayfalar_her_talebi_bir_kez_verir(karisik_depo, limit):
    assert await butun_sayfalar(karisik_depo, limit=limit) == [6, 3, 1, 5, 4, 2]


async def test_ayrac_var_olan_bir_talep_olmak_zorunda_degil(karisik_depo):
    sayfa = await karisik_depo.listele(sonra=Ayrac(T0 + timedelta(minutes=90), 999))
    assert numaralar(sayfa) == [5, 4, 2]


async def test_sayfalar_arasinda_eklenen_talep_kaydirmaz(depo):
    ilk = await depo.listele(limit=2)
    await depo.ekle(baslik="Yeni talep", musteri="ali@example.com", oncelik=Oncelik.ORTA, etiketler=[])
    ikinci = await depo.listele(limit=2, sonra=ilk.sonraki)
    assert numaralar(ikinci) == [3, 2]


async def test_listele_duruma_gore(depo):
    assert numaralar(await depo.listele(durum=Durum.ACIK)) == [5, 3, 1]


async def test_listele_oncelige_gore(depo):
    assert numaralar(await depo.listele(oncelik=Oncelik.YUKSEK)) == [3, 1]


async def test_listele_etikete_gore(depo):
    assert numaralar(await depo.listele(etiket="hesap")) == [3, 1]


async def test_listele_etiket_tam_eslesir(depo):
    assert numaralar(await depo.listele(etiket="hes")) == []


async def test_listele_filtreler_birlikte(depo):
    assert numaralar(await depo.listele(durum=Durum.ACIK, oncelik=Oncelik.ORTA)) == [5]


async def test_filtreler_sayfalarla_birlikte(depo):
    assert await butun_sayfalar(depo, limit=1, durum=Durum.ACIK) == [5, 3, 1]


async def test_listele_eslesme_yoksa_bos(depo):
    sayfa = await depo.listele(etiket="yok")
    assert sayfa.talepler == []
    assert sayfa.sonraki is None


async def test_listele_tirnakli_etiket_sorguyu_bozmaz(depo):
    assert numaralar(await depo.listele(etiket="hesap' OR '1'='1")) == []


async def test_listele_tam_talep_dondurur(depo):
    sayfa = await depo.listele(durum=Durum.BEKLEMEDE)
    assert sayfa.talepler == [ORNEKLER[3]]


# ara: tam metin arama, yalnız PostgreSQL'de (hazır verildi)

yalniz_pg = pytest.mark.parametrize("depo", ["pg"], indirect=True)


@yalniz_pg
async def test_ara_kelimeyi_bulur(depo):
    assert numaralar(await depo.listele(ara="şifre")) == [3]


@yalniz_pg
async def test_ara_buyuk_kucuk_harfe_bakmaz(depo):
    assert numaralar(await depo.listele(ara="KARGO")) == [5]


@yalniz_pg
async def test_ara_ekli_kelimeyi_bulur(depo):
    assert numaralar(await depo.listele(ara="kargom")) == [5]
    assert numaralar(await depo.listele(ara="şifremi")) == [3]


@yalniz_pg
async def test_ara_kelimelerin_hepsi_gecmeli(depo):
    assert numaralar(await depo.listele(ara="kargo numarası")) == [5]
    assert numaralar(await depo.listele(ara="kargo şifre")) == []


@yalniz_pg
async def test_ara_or_ve_eksi(depo):
    assert numaralar(await depo.listele(ara="kargo or şifre")) == [5, 3]
    assert numaralar(await depo.listele(ara="kargo -takip")) == []


@yalniz_pg
async def test_ara_tirnakli_ifade_sirayi_korur(depo):
    assert numaralar(await depo.listele(ara='"takip numarası"')) == [5]
    assert numaralar(await depo.listele(ara='"numarası takip"')) == []


@yalniz_pg
async def test_ara_durak_kelimesi_hata_vermez(depo):
    assert numaralar(await depo.listele(ara="ve")) == []


@yalniz_pg
async def test_ara_tirnak_ve_isaretler_sorguyu_bozmaz(depo):
    assert numaralar(await depo.listele(ara="kargo' OR '1'='1")) == [5]


@yalniz_pg
async def test_ara_filtreler_ve_sayfalarla_birlikte(depo):
    assert await butun_sayfalar(depo, limit=1, ara="gelmiyor or yapamıyorum") == [3, 1]
    assert numaralar(await depo.listele(ara="şifre", durum=Durum.KAPALI)) == []


@yalniz_pg
async def test_yeni_talep_aranabilir(depo):
    await depo.ekle(baslik="Kargom kayboldu", musteri="ali@example.com", oncelik=Oncelik.ORTA, etiketler=[])
    assert numaralar(await depo.listele(ara="kargo")) == [6, 5]


# guncelle: sürüm kontrollü (senin yazdığın)


async def test_guncelle_yalniz_durum(depo):
    talep = await depo.guncelle(1, surum=1, durum=Durum.KAPALI)
    assert talep is not None
    assert (talep.durum, talep.oncelik) == (Durum.KAPALI, Oncelik.YUKSEK)


async def test_guncelle_yalniz_oncelik(depo):
    talep = await depo.guncelle(4, surum=1, oncelik=Oncelik.YUKSEK)
    assert talep is not None
    assert (talep.durum, talep.oncelik) == (Durum.BEKLEMEDE, Oncelik.YUKSEK)


async def test_guncelle_ikisi_birden(depo):
    talep = await depo.guncelle(5, surum=1, durum=Durum.BEKLEMEDE, oncelik=Oncelik.DUSUK)
    assert talep is not None
    assert (talep.durum, talep.oncelik) == (Durum.BEKLEMEDE, Oncelik.DUSUK)


async def test_guncelle_surumu_bir_artirir(depo):
    talep = await depo.guncelle(1, surum=1, durum=Durum.BEKLEMEDE)
    assert talep is not None
    assert talep.surum == 2


async def test_guncelle_her_seferinde_bir_artirir(depo):
    for beklenen in (2, 3, 4):
        talep = await depo.guncelle(2, surum=beklenen - 1, oncelik=Oncelik.YUKSEK)
        assert talep is not None
        assert talep.surum == beklenen


async def test_guncelle_kalici(depo):
    await depo.guncelle(3, surum=1, durum=Durum.KAPALI)
    talep = await depo.getir(3)
    assert talep is not None
    assert (talep.durum, talep.surum) == (Durum.KAPALI, 2)


async def test_guncelle_diger_alanlari_ve_talepleri_degistirmez(depo):
    talep = await depo.guncelle(2, surum=1, durum=Durum.ACIK)
    assert talep is not None
    assert (talep.baslik, talep.musteri, talep.etiketler, talep.acildi) == (
        ORNEKLER[1].baslik,
        ORNEKLER[1].musteri,
        ORNEKLER[1].etiketler,
        ORNEKLER[1].acildi,
    )
    assert await depo.getir(1) == ORNEKLER[0]


async def test_listele_guncellemeden_sonra_sira_degismez(depo):
    await depo.guncelle(1, surum=1, durum=Durum.BEKLEMEDE)
    assert numaralar(await depo.listele()) == [5, 4, 3, 2, 1]


async def test_guncelle_olmayan_talepte_none(depo):
    assert await depo.guncelle(99, surum=1, durum=Durum.KAPALI) is None
    assert numaralar(await depo.listele()) == [5, 4, 3, 2, 1]


async def test_olmayan_talepte_surum_ne_olursa_olsun_none(depo):
    assert await depo.guncelle(99, surum=7, durum=Durum.KAPALI) is None


async def test_eski_surumle_guncelleme_cakisir(depo):
    await depo.guncelle(3, surum=1, durum=Durum.KAPALI)
    with pytest.raises(SurumCakismasi):
        await depo.guncelle(3, surum=1, durum=Durum.BEKLEMEDE)


async def test_ileri_bir_surum_de_cakisir(depo):
    with pytest.raises(SurumCakismasi):
        await depo.guncelle(1, surum=5, durum=Durum.KAPALI)


async def test_cakisma_guncel_talebi_tasir(depo):
    await depo.guncelle(3, surum=1, durum=Durum.KAPALI)
    with pytest.raises(SurumCakismasi) as bilgi:
        await depo.guncelle(3, surum=1, durum=Durum.BEKLEMEDE)
    guncel = bilgi.value.guncel
    assert (guncel.id, guncel.durum, guncel.surum) == (3, Durum.KAPALI, 2)


async def test_cakismada_hicbir_sey_yazilmaz(depo):
    await depo.guncelle(3, surum=1, durum=Durum.KAPALI)
    with pytest.raises(SurumCakismasi):
        await depo.guncelle(3, surum=1, durum=Durum.BEKLEMEDE, oncelik=Oncelik.DUSUK)
    talep = await depo.getir(3)
    assert talep is not None
    assert (talep.durum, talep.oncelik, talep.surum) == (Durum.KAPALI, Oncelik.YUKSEK, 2)


@pytest.mark.parametrize("depo", ["pg"], indirect=True)
async def test_ayni_anda_iki_guncellemeden_yalniz_biri_yazilir(depo):
    """Yalnız PostgreSQL'de: iki guncelle aynı sürümle, iki ayrı bağlantıdan, aynı anda."""
    for tur in range(1, 21):
        mevcut = await depo.getir(1)
        assert mevcut is not None
        sonuclar = await asyncio.gather(
            depo.guncelle(1, surum=mevcut.surum, durum=Durum.KAPALI),
            depo.guncelle(1, surum=mevcut.surum, oncelik=Oncelik.DUSUK),
            return_exceptions=True,
        )
        yazilan = [sonuc for sonuc in sonuclar if isinstance(sonuc, Talep)]
        cakisan = [sonuc for sonuc in sonuclar if isinstance(sonuc, SurumCakismasi)]
        assert (len(yazilan), len(cakisan)) == (1, 1), f"{tur}. tur: {sonuclar}"
        son = await depo.getir(1)
        assert son is not None
        assert son.surum == mevcut.surum + 1


# yorumlar (hazır verildi)


async def test_yorum_ekle_alanlari_doldurur(depo):
    yorum = await depo.yorum_ekle(3, yazan="ayse", metin="Müşteriyi aradım.")
    assert yorum is not None
    assert (yorum.id, yorum.talep_id, yorum.yazan, yorum.metin) == (1, 3, "ayse", "Müşteriyi aradım.")
    assert yorum.yazildi is not None


async def test_olmayan_talebe_yorum_eklenmez(depo):
    assert await depo.yorum_ekle(99, yazan="ayse", metin="Kayıp talep") is None


async def test_yorumlar_eklenme_sirasiyla(depo):
    await depo.yorum_ekle(1, yazan="ayse", metin="Birinci")
    await depo.yorum_ekle(1, yazan="mehmet", metin="İkinci")
    yorumlar = await depo.yorumlar(1)
    assert yorumlar is not None
    assert [(yorum.yazan, yorum.metin) for yorum in yorumlar] == [("ayse", "Birinci"), ("mehmet", "İkinci")]


async def test_yorumlar_yalniz_o_talebin(depo):
    await depo.yorum_ekle(1, yazan="ayse", metin="Bir")
    await depo.yorum_ekle(2, yazan="ayse", metin="İki")
    yorumlar = await depo.yorumlar(2)
    assert yorumlar is not None
    assert [yorum.metin for yorum in yorumlar] == ["İki"]


async def test_yorumsuz_talepte_bos_liste(depo):
    assert await depo.yorumlar(4) == []


async def test_olmayan_talebin_yorumlari_none(depo):
    assert await depo.yorumlar(99) is None
