from collections.abc import Iterable, Iterator
from pathlib import Path

from yardim_masasi.model import Durum, GecersizTalep, Talep, talepleri_oku


class TalepDeposu:
    """Talepleri numarasıyla, eklendikleri sırayla tutar."""

    def __init__(self, talepler: Iterable[Talep] = ()) -> None:
        self._talepler: dict[int, Talep] = {}
        for talep in talepler:
            self.ekle(talep)

    @classmethod
    def dosyadan(cls, yol: Path) -> TalepDeposu:
        return cls(talepleri_oku(yol))

    def ekle(self, talep: Talep) -> None:
        if talep.id in self._talepler:
            raise GecersizTalep(f"tekrarlanan id: {talep.id}")
        self._talepler[talep.id] = talep

    def __len__(self) -> int:
        return len(self._talepler)

    def __iter__(self) -> Iterator[Talep]:
        return iter(self._talepler.values())

    def __contains__(self, talep_id: object) -> bool:
        return talep_id in self._talepler

    def __getitem__(self, talep_id: int) -> Talep:
        return self._talepler[talep_id]

    def __repr__(self) -> str:
        return f"TalepDeposu({len(self)} talep)"

    @property
    def acik_sayisi(self) -> int:
        return sum(1 for talep in self if talep.durum == Durum.ACIK)

    def durumdakiler(self, durum: Durum) -> TalepDeposu:
        return TalepDeposu(talep for talep in self if talep.durum == durum)
