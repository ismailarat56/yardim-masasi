import json
from collections.abc import Iterable, Iterator
from pathlib import Path


class JsonSatirHatasi(ValueError):
    """JSON Lines dosyasında çözülemeyen bir satır."""

    def __init__(self, satir: int, sutun: int) -> None:
        super().__init__(f"{satir}. satır geçerli JSON değil (sütun {sutun})")
        self.satir = satir
        self.sutun = sutun


def satirlari_oku(yol: Path) -> Iterator[tuple[int, str]]:
    with yol.open(encoding="utf-8") as dosya:
        for numara, satir in enumerate(dosya, start=1):
            metin = satir.strip()
            if metin:
                yield numara, metin


def jsonl_oku(yol: Path) -> Iterator[object]:
    for numara, metin in satirlari_oku(yol):
        try:
            veri = json.loads(metin)
        except json.JSONDecodeError as hata:
            raise JsonSatirHatasi(numara, hata.colno) from hata
        yield veri


def parcalara_bol(ogeler: Iterable, boyut: int) -> Iterator[list]:
    if boyut < 1:
        raise ValueError("boyut en az 1 olmalı")
    return _parcalari_uret(ogeler, boyut)


def _parcalari_uret(ogeler: Iterable, boyut: int) -> Iterator[list]:
    parca = []
    for oge in ogeler:
        parca.append(oge)
        if len(parca) == boyut:
            yield parca
            parca = []
    if parca:
        yield parca
