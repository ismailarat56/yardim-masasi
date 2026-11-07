import argparse
import asyncio
import sys

import httpx

from yardim_masasi.pypi import ozet, paketleri_getir
from yardim_masasi.talepler import pozitif_tam_sayi


def arguman_ayristirici() -> argparse.ArgumentParser:
    ayristirici = argparse.ArgumentParser(
        prog="yardim-masasi",
        description="PyPI'daki paketlerin son sürümünü ve istediği Python sürümünü gösterir.",
    )
    ayristirici.add_argument("paketler", nargs="+", metavar="PAKET", help="sorulacak paketlerin adları")
    ayristirici.add_argument(
        "-e",
        "--eszamanli",
        type=pozitif_tam_sayi,
        default=4,
        metavar="N",
        help="aynı anda en fazla N istek (varsayılan: 4)",
    )
    return ayristirici


def main(argv: list[str] | None = None) -> int:
    args = arguman_ayristirici().parse_args(argv)
    try:
        sonuclar = asyncio.run(paketleri_getir(args.paketler, en_fazla=args.eszamanli))
    except* httpx.TransportError as grup:
        print(f"yardim-masasi: PyPI'a ulaşılamadı: {grup.exceptions[0]}", file=sys.stderr)
        raise SystemExit(1) from None

    kod = 0
    for paket, sonuc in zip(args.paketler, sonuclar, strict=True):
        if isinstance(sonuc, httpx.HTTPStatusError):
            print(f"yardim-masasi: {paket}: PyPI {sonuc.response.status_code} döndü", file=sys.stderr)
            kod = 1
        else:
            print(ozet(sonuc))
    return kod
