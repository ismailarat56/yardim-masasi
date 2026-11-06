import argparse
import logging
import sys
from collections import Counter, defaultdict
from datetime import timedelta
from importlib.metadata import version
from pathlib import Path

from yardim_masasi.depo import TalepDeposu
from yardim_masasi.filtre import filtrele
from yardim_masasi.metin import kisalt, kucuk_harf
from yardim_masasi.model import Durum, Oncelik, Talep, TalepHatasi

log = logging.getLogger(__name__)

VARSAYILAN_DOSYA = Path("ornek/talepler.json")
DURUMLAR = ("acik", "beklemede", "kapali")
ONCELIK_SIRASI = {"yuksek": 0, "orta": 1, "dusuk": 2}


def kapanmamislar(talepler: list[Talep]) -> list[Talep]:
    return [talep for talep in talepler if talep.durum != "kapali"]


def durum_sayilari(talepler: list[Talep]) -> dict[str, int]:
    sayac = Counter({durum: 0 for durum in Durum})
    sayac.update(t.durum for t in talepler)
    return {durum: sayac[durum] for durum in DURUMLAR}


def etiket_gruplari(talepler: list[Talep]) -> dict[str, list[int]]:
    gruplar: defaultdict[str, list[int]] = defaultdict(list)
    for talep in talepler:
        for etiket in talep.etiketler:
            gruplar[etiket].append(talep.id)
    return {etiket: gruplar[etiket] for etiket in sorted(gruplar)}


def oncelik_sirasi(talepler: list[Talep]) -> list[Talep]:
    return sorted(
        talepler,
        key=lambda talep: (ONCELIK_SIRASI[talep.oncelik], talep.id),
    )


def ara(talepler: list[Talep], *kelimeler: str, durum: str | None = None) -> list[int]:
    kucuk_kelimeler = [kucuk_harf(kelime) for kelime in kelimeler]
    bulunanlar = []
    for talep in talepler:
        if durum is not None and talep.durum != durum:
            continue
        baslik = kucuk_harf(talep.baslik)
        if all(kelime in baslik for kelime in kucuk_kelimeler):
            bulunanlar.append(talep.id)
    return bulunanlar


def ozet_satiri(talep: Talep) -> str:
    return (
        f"#{talep.id:>3} "
        f"{talep.oncelik:<6} "
        f"{talep.durum:<9} "
        f"{kisalt(talep.baslik, 30)}"
    )


def pozitif_tam_sayi(metin: str) -> int:
    try:
        sayi = int(metin)
    except ValueError:
        raise argparse.ArgumentTypeError(f"tam sayı bekleniyor: {metin!r}") from None
    if sayi < 1:
        raise argparse.ArgumentTypeError(f"en az 1 olmalı: {metin!r}")
    return sayi


def arguman_ayristirici() -> argparse.ArgumentParser:
    ayristirici = argparse.ArgumentParser(
        prog="talep-ozeti",
        description="Talep dosyasını özetler: durum sayıları ve kapanmamış talepler.",
    )
    ayristirici.add_argument(
        "dosya",
        nargs="?",
        type=Path,
        default=VARSAYILAN_DOSYA,
        help="okunacak .json ya da .jsonl dosyası (varsayılan: %(default)s)",
    )
    ayristirici.add_argument("--durum", type=Durum, choices=list(Durum), help="yalnızca bu durumdakiler")
    ayristirici.add_argument("--oncelik", type=Oncelik, choices=list(Oncelik), help="yalnızca bu öncelikteki talepler")
    ayristirici.add_argument("--etiket", help="yalnızca bu etiketi taşıyanlar")
    ayristirici.add_argument("--son-gun", type=pozitif_tam_sayi, metavar="N", help="yalnızca son N günde açılanlar")
    ayristirici.add_argument("-v", "--ayrintili", action="store_true", help="ayrıntılı günlük kayıtlarını stderr'e yaz")
    ayristirici.add_argument("--version", action="version", version=f"%(prog)s {version('yardim-masasi')}")
    return ayristirici


def main(argv: list[str] | None = None) -> int:
    args = arguman_ayristirici().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.ayrintili else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )
    try:
        depo = TalepDeposu.dosyadan(args.dosya)
    except TalepHatasi as hata:
        print(f"talep-ozeti: {hata}", file=sys.stderr)
        return 1
    log.debug("%d talep okundu", len(depo))
    secilenler = filtrele(
        depo,
        durum=args.durum,
        oncelik=args.oncelik,
        etiket=args.etiket,
        son=timedelta(days=args.son_gun) if args.son_gun is not None else None,
    )
    log.debug("Filtre sonrası %d talep kaldı", len(secilenler))
    sayilar = durum_sayilari(secilenler)
    print(", ".join(f"{durum}: {sayi}" for durum, sayi in sayilar.items()))
    print()
    listelenecekler = kapanmamislar(secilenler) if args.durum is None else secilenler
    for talep in oncelik_sirasi(listelenecekler):
        print(ozet_satiri(talep))
    return 0
