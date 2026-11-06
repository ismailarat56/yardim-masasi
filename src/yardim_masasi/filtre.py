from collections.abc import Iterable
from datetime import UTC, datetime, timedelta

from yardim_masasi.model import Durum, Oncelik, Talep


def filtrele(
    talepler: Iterable[Talep],
    *,
    durum: Durum | None = None,
    oncelik: Oncelik | None = None,
    etiket: str | None = None,
    son: timedelta | None = None,
    simdi: datetime | None = None,
) -> list[Talep]:
    if simdi is not None and simdi.utcoffset() is None:
        raise ValueError("simdi saat dilimi içermeli")
    if son is not None and son < timedelta(0):
        raise ValueError("son negatif olamaz")

    esik = None
    if son is not None:
        if simdi is None:
            simdi = datetime.now(UTC)
        esik = simdi - son

    def uyuyor_mu(talep: Talep) -> bool:
        if durum is not None and talep.durum != durum:
            return False
        if oncelik is not None and talep.oncelik != oncelik:
            return False
        if etiket is not None and etiket not in talep.etiketler:
            return False
        if esik is not None and (talep.acildi is None or talep.acildi < esik):
            return False
        return True

    return [talep for talep in talepler if uyuyor_mu(talep)]
