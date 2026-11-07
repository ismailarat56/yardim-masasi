from datetime import UTC, datetime, timedelta

import pytest

from yardim_masasi.filtre import filtrele
from yardim_masasi.model import Durum, Oncelik, Talep

SIMDI = datetime(2026, 11, 6, 12, 0, tzinfo=UTC)


def talep(id, durum=Durum.ACIK, oncelik=Oncelik.ORTA, etiketler=(), gun_once=None):
    acildi = None if gun_once is None else SIMDI - timedelta(days=gun_once)
    return Talep(
        id=id,
        baslik=f"Talep {id}",
        durum=durum,
        oncelik=oncelik,
        musteri="Ada",
        etiketler=etiketler,
        acildi=acildi,
    )


TALEPLER = [
    talep(1, Durum.ACIK, Oncelik.YUKSEK, ("giris",), gun_once=1),
    talep(2, Durum.KAPALI, Oncelik.DUSUK, ("fatura",), gun_once=10),
    talep(3, Durum.BEKLEMEDE, Oncelik.YUKSEK, ("giris", "mobil"), gun_once=3),
    talep(4, Durum.ACIK, Oncelik.ORTA),
    talep(5, Durum.ACIK, Oncelik.YUKSEK, ("mobil",), gun_once=8),
]


def idler(talepler):
    return [t.id for t in talepler]


def test_filtre_yoksa_hepsi_ayni_sirada():
    assert idler(filtrele(TALEPLER)) == [1, 2, 3, 4, 5]


def test_yeni_liste_doner():
    sonuc = filtrele(TALEPLER)
    assert sonuc == TALEPLER
    assert sonuc is not TALEPLER


@pytest.mark.parametrize(
    ("durum", "beklenen"),
    [(Durum.ACIK, [1, 4, 5]), (Durum.BEKLEMEDE, [3]), (Durum.KAPALI, [2])],
)
def test_duruma_gore(durum, beklenen):
    assert idler(filtrele(TALEPLER, durum=durum)) == beklenen


def test_oncelige_gore():
    assert idler(filtrele(TALEPLER, oncelik=Oncelik.YUKSEK)) == [1, 3, 5]


def test_etikete_gore():
    assert idler(filtrele(TALEPLER, etiket="mobil")) == [3, 5]


def test_filtreler_birlesir():
    sonuc = filtrele(TALEPLER, durum=Durum.ACIK, oncelik=Oncelik.YUKSEK, etiket="mobil")
    assert idler(sonuc) == [5]


def test_son_gunler():
    sonuc = filtrele(TALEPLER, son=timedelta(days=7), simdi=SIMDI)
    assert idler(sonuc) == [1, 3]


def test_sinirdaki_talep_dahil():
    sinirda = talep(9, gun_once=7)
    assert idler(filtrele([sinirda], son=timedelta(days=7), simdi=SIMDI)) == [9]


def test_ureteci_de_kabul_eder():
    sonuc = filtrele((t for t in TALEPLER), etiket="giris")
    assert idler(sonuc) == [1, 3]


def test_filtreler_konumsal_verilemez():
    with pytest.raises(TypeError):
        filtrele(TALEPLER, Durum.ACIK)  # pyright: ignore[reportCallIssue]


def test_naive_simdi_reddedilir():
    with pytest.raises(ValueError, match="saat dilimi"):
        filtrele(TALEPLER, son=timedelta(days=1), simdi=datetime(2026, 11, 6, 12, 0))


def test_negatif_sure_reddedilir():
    with pytest.raises(ValueError, match="negatif"):
        filtrele(TALEPLER, son=timedelta(days=-1), simdi=SIMDI)


def test_simdi_verilmezse_su_an_kullanilir():
    su_an = datetime.now(UTC)
    yeni = Talep(10, "Yeni", Durum.ACIK, Oncelik.ORTA, "Ada", (), su_an - timedelta(hours=1))
    eski = Talep(11, "Eski", Durum.ACIK, Oncelik.ORTA, "Ada", (), su_an - timedelta(days=30))
    assert idler(filtrele([yeni, eski], son=timedelta(days=7))) == [10]
