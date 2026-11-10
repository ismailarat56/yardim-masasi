"""Aynı sözleşme testleri bellek ve PostgreSQL depolarında koşar."""

import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import LiteralString, cast

import psycopg
import pytest
from psycopg_pool import AsyncConnectionPool

from sahte_depo import BellekDeposu
from yardim_masasi.model import Durum, Oncelik, Talep
from yardim_masasi.pg_depo import PgTalepDeposu
from yardim_masasi.veritabani import ornekleri_yukle

pytestmark = pytest.mark.anyio
TABLO_SQL = Path(__file__).parent.parent / "sql" / "001_talepler.sql"
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
    adres = os.environ.get("TEST_DATABASE_URL")
    if not adres:
        pytest.skip("TEST_DATABASE_URL tanımlı değil")
    with psycopg.connect(adres) as baglanti:
        # DROP yalnızca bu projeye ayrılan test veritabanında çalışabilir.
        if baglanti.info.dbname != "yardim_masasi_test":
            pytest.fail("TEST_DATABASE_URL yardim_masasi_test veritabanını göstermeli")
        baglanti.execute("DROP TABLE IF EXISTS talepler")
        baglanti.execute(cast(LiteralString, TABLO_SQL.read_text(encoding="utf-8")))
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


async def test_guncelle_yalniz_durum(depo):
    talep = await depo.guncelle(1, durum=Durum.KAPALI)
    assert talep is not None
    assert talep.durum == Durum.KAPALI
    assert talep.oncelik == Oncelik.YUKSEK


async def test_guncelle_yalniz_oncelik(depo):
    talep = await depo.guncelle(4, oncelik=Oncelik.YUKSEK)
    assert talep is not None
    assert talep.oncelik == Oncelik.YUKSEK
    assert talep.durum == Durum.BEKLEMEDE


async def test_guncelle_ikisi_birden(depo):
    talep = await depo.guncelle(5, durum=Durum.BEKLEMEDE, oncelik=Oncelik.DUSUK)
    assert talep is not None
    assert (talep.durum, talep.oncelik) == (Durum.BEKLEMEDE, Oncelik.DUSUK)


async def test_guncelle_kalici(depo):
    await depo.guncelle(3, durum=Durum.KAPALI)
    talep = await depo.getir(3)
    assert talep is not None
    assert talep.durum == Durum.KAPALI


async def test_guncelle_diger_alanlari_ve_talepleri_degistirmez(depo):
    talep = await depo.guncelle(2, durum=Durum.ACIK)
    assert talep is not None
    assert (talep.baslik, talep.musteri, talep.etiketler, talep.acildi) == (
        ORNEKLER[1].baslik, ORNEKLER[1].musteri, ORNEKLER[1].etiketler, ORNEKLER[1].acildi,
    )
    assert await depo.getir(1) == ORNEKLER[0]


async def test_listele_guncellemeden_sonra_da_numara_sirasiyla(depo):
    await depo.guncelle(1, durum=Durum.BEKLEMEDE)
    assert numaralar(await depo.listele()) == [1, 2, 3, 4, 5]


async def test_guncelle_olmayan_talepte_none(depo):
    assert await depo.guncelle(99, durum=Durum.KAPALI) is None
    assert numaralar(await depo.listele()) == [1, 2, 3, 4, 5]
