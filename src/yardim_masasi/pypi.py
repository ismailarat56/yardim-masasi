import functools
import os
from collections.abc import Iterable
from typing import Any

import httpx

from yardim_masasi.araclar import yeniden_dene
from yardim_masasi.eszamanli import sinirli_topla, yeniden_dene_async

PYPI_ADRESI = "https://pypi.org/pypi/{paket}/json"

type PaketSonucu = dict[str, Any] | httpx.HTTPStatusError


def zaman_asimi() -> float:
    return float(os.getenv("PYPI_ZAMAN_ASIMI", "10"))


@yeniden_dene(kez=3, hatalar=(httpx.TransportError,), bekleme=0.5)
def paket_bilgisi(paket: str) -> dict[str, Any]:
    yanit = httpx.get(PYPI_ADRESI.format(paket=paket), timeout=zaman_asimi())
    yanit.raise_for_status()
    return yanit.json()


@yeniden_dene_async(kez=3, hatalar=(httpx.TransportError,), bekleme=0.5)
async def paket_bilgisi_async(istemci: httpx.AsyncClient, paket: str) -> dict[str, Any]:
    yanit = await istemci.get(PYPI_ADRESI.format(paket=paket), timeout=zaman_asimi())
    yanit.raise_for_status()
    return yanit.json()


async def paketleri_getir(
    paketler: Iterable[str],
    *,
    en_fazla: int = 4,
    istemci: httpx.AsyncClient | None = None,
) -> list[PaketSonucu]:
    if istemci is None:
        async with httpx.AsyncClient() as yeni_istemci:
            return await paketleri_getir(paketler, en_fazla=en_fazla, istemci=yeni_istemci)

    async def getir(paket: str) -> PaketSonucu:
        try:
            return await paket_bilgisi_async(istemci, paket)
        except httpx.HTTPStatusError as hata:
            return hata

    return await sinirli_topla([functools.partial(getir, paket) for paket in paketler], en_fazla=en_fazla)


def ozet(veri: dict[str, Any]) -> str:
    bilgi = veri["info"]
    python = bilgi["requires_python"] or "belirtilmemiş"
    return f"{bilgi['name']} {bilgi['version']} (Python {python})"
