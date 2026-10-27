import sys

from yardim_masasi.pypi import ozet, paket_bilgisi


def main() -> None:
    for paket in sys.argv[1:]:
        print(ozet(paket_bilgisi(paket)))
