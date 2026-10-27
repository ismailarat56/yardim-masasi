def kucuk_harf(metin: str) -> str:
    return metin.replace("İ", "i").replace("I", "ı").lower()


def buyuk_harf(metin: str) -> str:
    return metin.replace("i", "İ").replace("ı", "I").upper()


def bosluklari_duzelt(metin: str) -> str:
    return " ".join(metin.split())


def etiketleri_ayir(metin: str) -> list[str]:
    etiketler = [
        kucuk_harf(bosluklari_duzelt(parca))
        for parca in metin.split(",")
    ]
    dolu_etiketler = [etiket for etiket in etiketler if etiket]
    return list(dict.fromkeys(dolu_etiketler))


def kisalt(metin: str, en_fazla: int = 30) -> str:
    if len(metin) <= en_fazla:
        return metin
    return metin[:en_fazla - 1].rstrip() + "…"


def maskele(eposta: str) -> str:
    ad, ayrac, alan = eposta.partition("@")
    if not ayrac or not ad or not alan:
        return "***"
    return f"{ad[0]}***@{alan}"
