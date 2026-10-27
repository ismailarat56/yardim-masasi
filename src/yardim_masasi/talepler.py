import json
import sys
from pathlib import Path

from yardim_masasi.metin import kisalt, kucuk_harf

DURUMLAR = ("acik", "beklemede", "kapali")
ONCELIK_SIRASI = {"yuksek": 0, "orta": 1, "dusuk": 2}


def kapanmamislar(talepler: list[dict]) -> list[dict]:
    return [talep for talep in talepler if talep["durum"] != "kapali"]


def durum_sayilari(talepler: list[dict]) -> dict[str, int]:
    return {
        durum: sum(1 for talep in talepler if talep["durum"] == durum)
        for durum in DURUMLAR
    }


def etiket_gruplari(talepler: list[dict]) -> dict[str, list[int]]:
    gruplar: dict[str, list[int]] = {}
    for talep in talepler:
        for etiket in talep["etiketler"]:
            gruplar.setdefault(etiket, []).append(talep["id"])
    return {etiket: gruplar[etiket] for etiket in sorted(gruplar)}


def oncelik_sirasi(talepler: list[dict]) -> list[dict]:
    return sorted(
        talepler,
        key=lambda talep: (ONCELIK_SIRASI[talep["oncelik"]], talep["id"]),
    )


def ara(talepler: list[dict], *kelimeler: str, durum: str | None = None) -> list[int]:
    kucuk_kelimeler = [kucuk_harf(kelime) for kelime in kelimeler]
    bulunanlar = []
    for talep in talepler:
        if durum is not None and talep["durum"] != durum:
            continue
        baslik = kucuk_harf(talep["baslik"])
        if all(kelime in baslik for kelime in kucuk_kelimeler):
            bulunanlar.append(talep["id"])
    return bulunanlar


def ozet_satiri(talep: dict) -> str:
    return (
        f"#{talep['id']:>3} "
        f"{talep['oncelik']:<6} "
        f"{talep['durum']:<9} "
        f"{kisalt(talep['baslik'], 30)}"
    )


def main() -> None:
    yol = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ornek/talepler.json")
    talepler = json.loads(yol.read_text(encoding="utf-8"))
    sayilar = durum_sayilari(talepler)
    print(", ".join(f"{durum}: {sayi}" for durum, sayi in sayilar.items()))
    print()
    for talep in oncelik_sirasi(kapanmamislar(talepler)):
        print(ozet_satiri(talep))
