import base64
import re
from datetime import UTC, datetime, timedelta, timezone

import pytest

from yardim_masasi.model import Durum, Oncelik, Talep
from yardim_masasi.sayfa import Ayrac, GecersizAyrac, ayrac_oku, ayrac_yaz

T0 = datetime(2026, 11, 1, 9, 0, tzinfo=UTC)


def kodla(metin: str) -> str:
    return base64.urlsafe_b64encode(metin.encode()).decode().rstrip("=")


def test_gidis_donus():
    ayrac = Ayrac(T0, 42)
    assert ayrac_oku(ayrac_yaz(ayrac)) == ayrac


def test_saat_dilimi_korunur():
    istanbul = timezone(timedelta(hours=3))
    ayrac = Ayrac(datetime(2026, 10, 21, 10, 0, 0, 123456, tzinfo=istanbul), 1)
    okunan = ayrac_oku(ayrac_yaz(ayrac))
    assert okunan == ayrac
    assert okunan.acildi.utcoffset() == timedelta(hours=3)


def test_ayrac_adreste_kacissiz_kullanilir():
    metin = ayrac_yaz(Ayrac(T0 + timedelta(microseconds=999), 10012))
    assert re.fullmatch(r"[A-Za-z0-9_-]+", metin)


def test_talepten_son_talebin_zamani_ve_numarasi():
    talep = Talep(7, "Fatura gelmedi", Durum.ACIK, Oncelik.ORTA, "ela@example.com", (), T0)
    assert Ayrac.talepten(talep) == Ayrac(T0, 7)


def test_zamansiz_talepten_ayrac_olmaz():
    talep = Talep(7, "Fatura gelmedi", Durum.ACIK, Oncelik.ORTA, "ela@example.com")
    with pytest.raises(ValueError):
        Ayrac.talepten(talep)


@pytest.mark.parametrize(
    "metin",
    [
        "",
        "abc",
        "!!!!",
        "şifre",
        kodla("merhaba"),
        kodla("[1, 2]"),
        kodla('{"i": 5}'),
        kodla('{"a": 5, "i": 5}'),
        kodla('{"a": "dün", "i": 5}'),
        kodla('{"a": "2026-11-01T09:00:00", "i": 5}'),
        kodla('{"a": "2026-11-01T09:00:00+00:00", "i": 0}'),
        kodla('{"a": "2026-11-01T09:00:00+00:00", "i": "5"}'),
        kodla('{"a": "2026-11-01T09:00:00+00:00", "i": true}'),
    ],
)
def test_bozuk_ayrac_reddedilir(metin):
    with pytest.raises(GecersizAyrac):
        ayrac_oku(metin)
