from collections.abc import Mapping
from typing import Any, Final

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from yardim_masasi.model import Durum, Oncelik, SurumCakismasi, Talep, Yorum
from yardim_masasi.sayfa import Ayrac, Sayfa

SUTUNLAR: Final = "id, baslik, durum, oncelik, musteri, etiketler, acildi, surum"
YORUM_SUTUNLARI: Final = "id, talep_id, yazan, metin, yazildi"


def talep_satirdan(satir: Mapping[str, Any]) -> Talep:
    return Talep(
        id=satir["id"], baslik=satir["baslik"], durum=Durum(satir["durum"]),
        oncelik=Oncelik(satir["oncelik"]), musteri=satir["musteri"],
        etiketler=tuple(satir["etiketler"]), acildi=satir["acildi"],
        surum=satir["surum"],
    )


def yorum_satirdan(satir: Mapping[str, Any]) -> Yorum:
    return Yorum(
        id=satir["id"],
        talep_id=satir["talep_id"],
        yazan=satir["yazan"],
        metin=satir["metin"],
        yazildi=satir["yazildi"],
    )


class PgTalepDeposu:
    """Talepleri PostgreSQL'deki talepler tablosunda tutar."""

    def __init__(self, havuz: AsyncConnectionPool) -> None:
        self._havuz = havuz

    async def getir(self, talep_id: int) -> Talep | None:
        async with self._havuz.connection() as baglanti:
            async with baglanti.cursor(row_factory=dict_row) as imlec:
                await imlec.execute(f"SELECT {SUTUNLAR} FROM talepler WHERE id = %s", (talep_id,))
                satir = await imlec.fetchone()
        return None if satir is None else talep_satirdan(satir)

    async def ekle(self, *, baslik: str, musteri: str, oncelik: Oncelik, etiketler: list[str]) -> Talep:
        async with self._havuz.connection() as baglanti:
            async with baglanti.cursor(row_factory=dict_row) as imlec:
                await imlec.execute(
                    f"""
                    INSERT INTO talepler (baslik, musteri, oncelik, etiketler)
                    VALUES (%s, %s, %s, %s)
                    RETURNING {SUTUNLAR}
                    """, (baslik, musteri, oncelik, etiketler),
                )
                satir = await imlec.fetchone()
        if satir is None:
            raise RuntimeError("INSERT satır döndürmedi")
        return talep_satirdan(satir)

    async def durum_sayilari(self) -> dict[Durum, int]:
        sayilar = {durum: 0 for durum in Durum}
        async with self._havuz.connection() as baglanti:
            async with baglanti.cursor(row_factory=dict_row) as imlec:
                await imlec.execute("SELECT durum, count(*) AS sayi FROM talepler GROUP BY durum")
                async for satir in imlec:
                    sayilar[Durum(satir["durum"])] = satir["sayi"]
        return sayilar

    async def listele(
        self,
        *,
        durum: Durum | None = None,
        oncelik: Oncelik | None = None,
        etiket: str | None = None,
        ara: str | None = None,
        sonra: Ayrac | None = None,
        limit: int = 20,
    ) -> Sayfa:
        arama_kosulu = "" if ara is None else "AND arama @@ websearch_to_tsquery('turkish', %(ara)s)"
        ayrac_kosulu = "" if sonra is None else "AND (acildi, id) < (%(acildi)s, %(id)s)"
        async with self._havuz.connection() as baglanti:
            async with baglanti.cursor(row_factory=dict_row) as imlec:
                await imlec.execute(
                    f"""
                    SELECT {SUTUNLAR} FROM talepler
                    WHERE (%(durum)s::text IS NULL OR durum = %(durum)s)
                      AND (%(oncelik)s::text IS NULL OR oncelik = %(oncelik)s)
                      AND (%(etiket)s::text IS NULL OR %(etiket)s = ANY (etiketler))
                      {arama_kosulu}
                      {ayrac_kosulu}
                    ORDER BY acildi DESC, id DESC
                    LIMIT %(limit)s
                    """,
                    {
                        "durum": durum,
                        "oncelik": oncelik,
                        "etiket": etiket,
                        "ara": ara,
                        "acildi": None if sonra is None else sonra.acildi,
                        "id": None if sonra is None else sonra.id,
                        "limit": limit + 1,
                    },
                )
                satirlar = await imlec.fetchall()
        talepler = [talep_satirdan(satir) for satir in satirlar[:limit]]
        sonraki = Ayrac.talepten(talepler[-1]) if len(satirlar) > limit else None
        return Sayfa(talepler, sonraki)

    async def guncelle(
        self,
        talep_id: int,
        *,
        surum: int,
        durum: Durum | None = None,
        oncelik: Oncelik | None = None,
    ) -> Talep | None:
        mevcut = None
        async with self._havuz.connection() as baglanti:
            async with baglanti.cursor(row_factory=dict_row) as imlec:
                # Kontrol ve yazma tek komutta: sürüm tutmazsa WHERE satırı seçmez, hiçbir şey yazılmaz.
                await imlec.execute(
                    f"""
                    UPDATE talepler
                    SET durum = coalesce(%(durum)s, durum),
                        oncelik = coalesce(%(oncelik)s, oncelik),
                        surum = surum + 1
                    WHERE id = %(talep_id)s AND surum = %(surum)s
                    RETURNING {SUTUNLAR}
                    """,
                    {"talep_id": talep_id, "surum": surum, "durum": durum, "oncelik": oncelik},
                )
                satir = await imlec.fetchone()
                if satir is None:
                    # Satır gelmedi: ya talep yok ya da sürüm tutmadı. Hangisi olduğunu öğren.
                    await imlec.execute(f"SELECT {SUTUNLAR} FROM talepler WHERE id = %s", (talep_id,))
                    mevcut = await imlec.fetchone()
        if satir is not None:
            return talep_satirdan(satir)
        if mevcut is None:
            return None
        raise SurumCakismasi(talep_satirdan(mevcut))

    async def yorum_ekle(self, talep_id: int, *, yazan: str, metin: str) -> Yorum | None:
        try:
            async with self._havuz.connection() as baglanti:
                async with baglanti.cursor(row_factory=dict_row) as imlec:
                    await imlec.execute(
                        f"""
                        INSERT INTO yorumlar (talep_id, yazan, metin)
                        VALUES (%s, %s, %s)
                        RETURNING {YORUM_SUTUNLARI}
                        """,
                        (talep_id, yazan, metin),
                    )
                    satir = await imlec.fetchone()
        except psycopg.errors.ForeignKeyViolation:
            return None
        if satir is None:
            raise RuntimeError("INSERT satır döndürmedi")
        return yorum_satirdan(satir)

    async def yorumlar(self, talep_id: int) -> list[Yorum] | None:
        async with self._havuz.connection() as baglanti:
            async with baglanti.cursor(row_factory=dict_row) as imlec:
                await imlec.execute("SELECT 1 FROM talepler WHERE id = %s", (talep_id,))
                if await imlec.fetchone() is None:
                    return None
                await imlec.execute(
                    f"SELECT {YORUM_SUTUNLARI} FROM yorumlar WHERE talep_id = %s ORDER BY id",
                    (talep_id,),
                )
                return [yorum_satirdan(satir) async for satir in imlec]
