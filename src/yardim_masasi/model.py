import json
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path

from yardim_masasi.akis import JsonSatirHatasi, jsonl_oku


class TalepHatasi(Exception):
    """Talep verisiyle ilgili bütün hataların atası."""


class GecersizTalep(TalepHatasi):
    """Bir talep sözleşmeye uymuyor."""


class TalepDosyasiHatasi(TalepHatasi):
    """Talep dosyası okunamıyor ya da bir talep listesi içermiyor."""


class Durum(StrEnum):
    ACIK = "acik"
    BEKLEMEDE = "beklemede"
    KAPALI = "kapali"


class Oncelik(StrEnum):
    YUKSEK = "yuksek"
    ORTA = "orta"
    DUSUK = "dusuk"


ZORUNLU_ALANLAR = ("id", "baslik", "durum", "oncelik", "musteri")


def _zaman_coz(deger: object) -> datetime | None:
    if deger is None:
        return None
    if not isinstance(deger, str):
        raise GecersizTalep(f"acildi metin olmalı: {deger!r}")

    try:
        zaman = datetime.fromisoformat(deger)
    except ValueError:
        raise GecersizTalep(f"geçersiz acildi: {deger!r}") from None

    if zaman.utcoffset() is None:
        raise GecersizTalep(f"acildi saat dilimi içermeli: {deger!r}")
    return zaman


@dataclass(frozen=True)
class Talep:
    id: int
    baslik: str
    durum: Durum
    oncelik: Oncelik
    musteri: str
    etiketler: tuple[str, ...] = ()
    acildi: datetime | None = None
    surum: int = 1

    @classmethod
    def sozlukten(cls, veri: dict) -> Talep:
        if not isinstance(veri, dict):
            raise GecersizTalep("talep bir JSON nesnesi olmalı")

        for alan in ZORUNLU_ALANLAR:
            if alan not in veri:
                raise GecersizTalep(f"eksik alan: {alan}")

        if not isinstance(veri["id"], int) or veri["id"] <= 0:
            raise GecersizTalep(f"geçersiz id: {veri['id']!r}")

        if not isinstance(veri["baslik"], str) or not veri["baslik"].strip():
            raise GecersizTalep("başlık boş olamaz")

        try:
            durum = Durum(veri["durum"])
        except ValueError as hata:
            raise GecersizTalep(f"bilinmeyen durum: {veri['durum']!r}") from hata

        try:
            oncelik = Oncelik(veri["oncelik"])
        except ValueError as hata:
            raise GecersizTalep(f"bilinmeyen öncelik: {veri['oncelik']!r}") from hata

        if not isinstance(veri["musteri"], str) or "@" not in veri["musteri"]:
            raise GecersizTalep(f"geçersiz müşteri: {veri['musteri']!r}")

        etiketler = veri.get("etiketler", [])
        if not isinstance(etiketler, list) or not all(
            isinstance(etiket, str) for etiket in etiketler
        ):
            raise GecersizTalep("etiketler bir metin listesi olmalı")

        return cls(
            id=veri["id"],
            baslik=veri["baslik"],
            durum=durum,
            oncelik=oncelik,
            musteri=veri["musteri"],
            etiketler=tuple(etiketler),
            acildi=_zaman_coz(veri.get("acildi")),
        )


def _dosyadaki_ogeler(yol: Path) -> list:
    try:
        if yol.suffix == ".jsonl":
            return list(jsonl_oku(yol))
        metin = yol.read_text(encoding="utf-8")
    except FileNotFoundError as hata:
        raise TalepDosyasiHatasi(f"dosya bulunamadı: {yol}") from hata
    except OSError as hata:
        raise TalepDosyasiHatasi(f"dosya okunamadı: {yol}") from hata
    except JsonSatirHatasi as hata:
        raise TalepDosyasiHatasi(
            f"geçerli JSON değil: {yol} "
            f"(satır {hata.satir}, sütun {hata.sutun})"
        ) from hata

    try:
        veri = json.loads(metin)
    except json.JSONDecodeError as hata:
        raise TalepDosyasiHatasi(
            f"geçerli JSON değil: {yol} "
            f"(satır {hata.lineno}, sütun {hata.colno})"
        ) from hata

    if not isinstance(veri, list):
        raise TalepDosyasiHatasi(f"talep listesi bekleniyordu: {yol}")
    return veri


def talepleri_oku(yol: Path) -> list[Talep]:
    talepler = []
    gorulen = set()

    for sira, oge in enumerate(_dosyadaki_ogeler(yol), start=1):
        try:
            talep = Talep.sozlukten(oge)
        except GecersizTalep as hata:
            raise GecersizTalep(f"{sira}. talep: {hata}") from hata

        if talep.id in gorulen:
            raise GecersizTalep(f"{sira}. talep: tekrarlanan id: {talep.id}")

        gorulen.add(talep.id)
        talepler.append(talep)

    return talepler
