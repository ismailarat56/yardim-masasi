from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from yardim_masasi.model import GecersizTalep, Talep, talepleri_oku

KOK = Path(__file__).resolve().parent.parent


def veri(**ek):
    temel = {
        "id": 1,
        "baslik": "Giriş yapamıyorum",
        "durum": "acik",
        "oncelik": "yuksek",
        "musteri": "ada@example.com",
        "etiketler": ["giris"],
    }
    temel.update(ek)
    return temel


def test_acildi_yoksa_none():
    assert Talep.sozlukten(veri()).acildi is None


def test_acildi_saat_dilimiyle_okunur():
    talep = Talep.sozlukten(veri(acildi="2026-11-02T09:30:00+03:00"))
    assert talep.acildi == datetime(2026, 11, 2, 6, 30, tzinfo=timezone.utc)
    assert talep.acildi.utcoffset() == timedelta(hours=3)


def test_z_utc_demek():
    talep = Talep.sozlukten(veri(acildi="2026-11-02T06:30:00Z"))
    assert talep.acildi.utcoffset() == timedelta(0)


@pytest.mark.parametrize(
    "deger",
    ["2026-11-02T09:30:00", "dün", "2026-13-01T00:00:00+03:00", 1730000000],
)
def test_gecersiz_acildi_reddedilir(deger):
    with pytest.raises(GecersizTalep, match="acildi"):
        Talep.sozlukten(veri(acildi=deger))


def test_zamanli_ornek_dosya_okunur():
    talepler = talepleri_oku(KOK / "ornek" / "talepler-zamanli.jsonl")
    assert len(talepler) == 12
    assert all(t.acildi is not None for t in talepler)
