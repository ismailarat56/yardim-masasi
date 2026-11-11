"""Aynı sözleşme testleri bellek ve PostgreSQL depolarında koşar."""

import asyncio
from datetime import UTC, datetime, timedelta

import psycopg
import pytest
from psycopg_pool import AsyncConnectionPool

from sahte_depo import BellekDeposu
from yardim_masasi.model import Durum, Oncelik, SurumCakismasi, Talep
from yardim_masasi.pg_depo import PgTalepDeposu
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


@pytest.fixture(params=["bellek", "pg"])
async def depo(request):
    if request.param == "bellek":
        yield BellekDeposu(ORNEKLER)
        return
    adres = request.getfixturevalue("test_adresi")
    with psycopg.connect(adres) as baglanti:
        baglanti.execute("TRUNCATE talepler RESTART IDENTITY CASCADE")
        ornekleri_yukle(baglanti, ORNEKLER)
    havuz = AsyncConnectionPool(adres, connection_class=psycopg.AsyncConnection, min_size=1, max_size=2, open=False)
    await havuz.open(wait=True, timeout=5)
    try:
        yield PgTalepDeposu(havuz)
    finally:
        await havuz.close()


def numaralar(talepler):
    return [talep.id for talep in talepler]


async def test_getir_talebi_bulur(depo):
    assert await depo.getir(1) == ORNEKLER[0]


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


async def test_listele_hepsini_numara_sirasiyla_verir(depo):
    assert numaralar(await depo.listele()) == [1, 2, 3, 4, 5]


async def test_listele_duruma_gore(depo):
    assert numaralar(await depo.listele(durum=Durum.ACIK)) == [1, 3, 5]


async def test_listele_oncelige_gore(depo):
    assert numaralar(await depo.listele(oncelik=Oncelik.YUKSEK)) == [1, 3]


async def test_listele_etikete_gore(depo):
    assert numaralar(await depo.listele(etiket="hesap")) == [1, 3]


async def test_listele_etiket_tam_eslesir(depo):
    assert await depo.listele(etiket="hes") == []


async def test_listele_filtreler_birlikte(depo):
    assert numaralar(await depo.listele(durum=Durum.ACIK, oncelik=Oncelik.ORTA)) == [5]


async def test_listele_eslesme_yoksa_bos(depo):
    assert await depo.listele(etiket="yok") == []


async def test_listele_tirnakli_etiket_sorguyu_bozmaz(depo):
    assert await depo.listele(etiket="hesap' OR '1'='1") == []


async def test_listele_tam_talep_dondurur(depo):
    assert await depo.listele(durum=Durum.BEKLEMEDE) == [ORNEKLER[3]]


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


async def test_listele_guncellemeden_sonra_da_numara_sirasiyla(depo):
    await depo.guncelle(1, surum=1, durum=Durum.BEKLEMEDE)
    assert numaralar(await depo.listele()) == [1, 2, 3, 4, 5]


async def test_guncelle_olmayan_talepte_none(depo):
    assert await depo.guncelle(99, surum=1, durum=Durum.KAPALI) is None
    assert numaralar(await depo.listele()) == [1, 2, 3, 4, 5]


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
