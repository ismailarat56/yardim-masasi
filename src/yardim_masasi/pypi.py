import os

import httpx

PYPI_ADRESI = "https://pypi.org/pypi/{paket}/json"


def zaman_asimi() -> float:
    return float(os.getenv("PYPI_ZAMAN_ASIMI", "10"))


def paket_bilgisi(paket: str) -> dict:
    yanit = httpx.get(PYPI_ADRESI.format(paket=paket), timeout=zaman_asimi())
    yanit.raise_for_status()
    return yanit.json()


def ozet(veri: dict) -> str:
    bilgi = veri["info"]
    python = bilgi["requires_python"] or "belirtilmemiş"
    return f"{bilgi['name']} {bilgi['version']} (Python {python})"
