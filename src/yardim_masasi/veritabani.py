import os
import sys
from collections.abc import Iterable
from pathlib import Path

import psycopg

from yardim_masasi.model import Talep, TalepHatasi, talepleri_oku

EKLE_SQL = """
    INSERT INTO talepler (id, baslik, durum, oncelik, musteri, etiketler, acildi)
    VALUES (%s, %s, %s, %s, %s, %s, coalesce(%s, now()))
"""

SAYACI_AYARLA_SQL = """
    SELECT setval(pg_get_serial_sequence('talepler', 'id'), (SELECT max(id) FROM talepler))
"""


def baglanti_adresi(degisken: str = "DATABASE_URL") -> str:
    adres = os.environ.get(degisken)
    if not adres:
        raise RuntimeError(f"{degisken} tanımlı değil")
    return adres


def ornekleri_yukle(baglanti: psycopg.Connection, talepler: Iterable[Talep]) -> int:
    sayi = 0
    with baglanti.cursor() as imlec:
        for talep in talepler:
            imlec.execute(
                EKLE_SQL,
                (
                    talep.id,
                    talep.baslik,
                    talep.durum,
                    talep.oncelik,
                    talep.musteri,
                    list(talep.etiketler),
                    talep.acildi,
                ),
            )
            sayi += 1
        imlec.execute(SAYACI_AYARLA_SQL)
    return sayi


def main() -> int:
    dosya = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ornek/talepler-zamanli.jsonl")
    try:
        talepler = talepleri_oku(dosya)
        with psycopg.connect(baglanti_adresi()) as baglanti:
            mevcut = baglanti.execute("SELECT count(*) FROM talepler").fetchone()
            if mevcut is not None and mevcut[0] > 0:
                print(f"talep-yukle: tablo boş değil ({mevcut[0]} talep var)", file=sys.stderr)
                return 1
            sayi = ornekleri_yukle(baglanti, talepler)
    except (TalepHatasi, RuntimeError, psycopg.Error) as hata:
        print(f"talep-yukle: {hata}", file=sys.stderr)
        return 1
    print(f"{sayi} talep yüklendi")
    return 0
