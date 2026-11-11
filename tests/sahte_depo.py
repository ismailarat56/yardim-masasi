from collections.abc import Iterable
from dataclasses import replace
from datetime import UTC, datetime

from yardim_masasi.model import Durum, Oncelik, SurumCakismasi, Talep, Yorum


class BellekDeposu:
    """PgTalepDeposu ile aynı sözleşmeyi uygulayan test deposu."""

    def __init__(self, talepler: Iterable[Talep] = ()) -> None:
        self._talepler = {talep.id: talep for talep in talepler}
        self._yorumlar: list[Yorum] = []

    async def getir(self, talep_id: int) -> Talep | None:
        return self._talepler.get(talep_id)

    async def ekle(self, *, baslik: str, musteri: str, oncelik: Oncelik, etiketler: list[str]) -> Talep:
        yeni_id = max(self._talepler, default=0) + 1
        talep = Talep(yeni_id, baslik, Durum.ACIK, oncelik, musteri, tuple(etiketler), datetime.now(UTC))
        self._talepler[yeni_id] = talep
        return talep

    async def durum_sayilari(self) -> dict[Durum, int]:
        sayilar = {durum: 0 for durum in Durum}
        for talep in self._talepler.values():
            sayilar[talep.durum] += 1
        return sayilar

    async def listele(
        self, *, durum: Durum | None = None, oncelik: Oncelik | None = None,
        etiket: str | None = None,
    ) -> list[Talep]:
        return [
            talep for talep in sorted(self._talepler.values(), key=lambda t: t.id)
            if (durum is None or talep.durum == durum)
            and (oncelik is None or talep.oncelik == oncelik)
            and (etiket is None or etiket in talep.etiketler)
        ]

    async def guncelle(
        self,
        talep_id: int,
        *,
        surum: int,
        durum: Durum | None = None,
        oncelik: Oncelik | None = None,
    ) -> Talep | None:
        talep = self._talepler.get(talep_id)
        if talep is None:
            return None
        if talep.surum != surum:
            raise SurumCakismasi(talep)
        yeni = replace(
            talep,
            durum=durum or talep.durum,
            oncelik=oncelik or talep.oncelik,
            surum=talep.surum + 1,
        )
        self._talepler[talep_id] = yeni
        return yeni

    async def yorum_ekle(self, talep_id: int, *, yazan: str, metin: str) -> Yorum | None:
        if talep_id not in self._talepler:
            return None
        yorum = Yorum(len(self._yorumlar) + 1, talep_id, yazan, metin, datetime.now(UTC))
        self._yorumlar.append(yorum)
        return yorum

    async def yorumlar(self, talep_id: int) -> list[Yorum] | None:
        if talep_id not in self._talepler:
            return None
        return [yorum for yorum in self._yorumlar if yorum.talep_id == talep_id]
