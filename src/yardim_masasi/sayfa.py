"""Ayraçlı sayfalama: bir sayfanın son talebini istemciye opak bir metin olarak verir."""

import base64
import binascii
import json
from dataclasses import dataclass
from datetime import datetime

from yardim_masasi.model import Talep


class GecersizAyrac(ValueError):
    """Metin bu API'nin verdiği bir ayraç değil ya da bozulmuş."""


@dataclass(frozen=True)
class Ayrac:
    """Bir sayfanın son talebi. Sonraki sayfa (acildi, id) çifti bundan küçük olanlarla başlar."""

    acildi: datetime
    id: int

    @classmethod
    def talepten(cls, talep: Talep) -> Ayrac:
        if talep.acildi is None:
            raise ValueError(f"{talep.id} numaralı talebin açılış zamanı yok")
        return cls(talep.acildi, talep.id)


@dataclass(frozen=True)
class Sayfa:
    talepler: list[Talep]
    sonraki: Ayrac | None


def ayrac_yaz(ayrac: Ayrac) -> str:
    veri = json.dumps({"a": ayrac.acildi.isoformat(), "i": ayrac.id}, separators=(",", ":"))
    return base64.urlsafe_b64encode(veri.encode()).decode().rstrip("=")


def ayrac_oku(metin: str) -> Ayrac:
    try:
        ham = base64.b64decode(metin + "=" * (-len(metin) % 4), altchars=b"-_", validate=True)
        veri = json.loads(ham)
        acildi = datetime.fromisoformat(veri["a"])
        talep_id = veri["i"]
    except (binascii.Error, ValueError, KeyError, TypeError) as hata:
        raise GecersizAyrac("ayraç okunamadı") from hata
    if acildi.utcoffset() is None or type(talep_id) is not int or talep_id < 1:
        raise GecersizAyrac("ayraç okunamadı")
    return Ayrac(acildi, talep_id)
