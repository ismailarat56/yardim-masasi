from pathlib import Path

import pytest

from yardim_masasi.depo import TalepDeposu
from yardim_masasi.model import Durum, GecersizTalep, Oncelik, Talep, TalepDosyasiHatasi
from yardim_masasi.talepler import durum_sayilari, kapanmamislar

ORNEK = Path(__file__).parent.parent / "ornek" / "talepler.json"


def talep(talep_id, durum=Durum.ACIK):
    return Talep(talep_id, f"Talep {talep_id}", durum, Oncelik.ORTA, "ayse@example.com")


def test_bos_depo():
    depo = TalepDeposu()
    assert len(depo) == 0
    assert not depo
    assert list(depo) == []


def test_ekle_ve_numarayla_bul():
    depo = TalepDeposu()
    ilk = talep(5)
    depo.ekle(ilk)
    assert len(depo) == 1
    assert depo
    assert 5 in depo
    assert depo[5] is ilk


def test_olmayan_numara():
    depo = TalepDeposu([talep(5)])
    assert 99 not in depo
    assert "5" not in depo
    with pytest.raises(KeyError):
        depo[99]


def test_tekrarlanan_id():
    depo = TalepDeposu([talep(5)])
    with pytest.raises(GecersizTalep) as bilgi:
        depo.ekle(talep(5, Durum.KAPALI))
    assert str(bilgi.value) == "tekrarlanan id: 5"
    assert len(depo) == 1
    assert depo[5].durum == Durum.ACIK


def test_kurucuda_tekrarlanan_id():
    with pytest.raises(GecersizTalep):
        TalepDeposu([talep(1), talep(1)])


def test_eklenme_sirasi():
    depo = TalepDeposu([talep(3), talep(1), talep(2)])
    assert [t.id for t in depo] == [3, 1, 2]


def test_iki_kez_dolasilir():
    depo = TalepDeposu([talep(1), talep(2)])
    assert [t.id for t in depo] == [1, 2]
    assert [t.id for t in depo] == [1, 2]


def test_uretecle_kurulur():
    depo = TalepDeposu(talep(i) for i in range(1, 4))
    assert len(depo) == 3


def test_verilen_listeyi_saklamaz():
    liste = [talep(1)]
    depo = TalepDeposu(liste)
    liste.append(talep(2))
    assert len(depo) == 1


def test_repr():
    assert repr(TalepDeposu()) == "TalepDeposu(0 talep)"
    assert repr(TalepDeposu([talep(1), talep(2)])) == "TalepDeposu(2 talep)"


def test_dosyadan():
    depo = TalepDeposu.dosyadan(ORNEK)
    assert len(depo) == 12
    assert depo[4].baslik == "Ödeme iki kez çekildi"


def test_dosyadan_alt_sinifi_dondurur():
    class ArsivDeposu(TalepDeposu):
        pass

    depo = ArsivDeposu.dosyadan(ORNEK)
    assert type(depo) is ArsivDeposu


def test_dosyadan_hatayi_gecirir(tmp_path):
    with pytest.raises(TalepDosyasiHatasi):
        TalepDeposu.dosyadan(tmp_path / "yok.json")


def test_acik_sayisi():
    depo = TalepDeposu.dosyadan(ORNEK)
    assert depo.acik_sayisi == 6
    depo.ekle(talep(13))
    assert depo.acik_sayisi == 7


def test_acik_sayisi_atanamaz():
    depo = TalepDeposu()
    with pytest.raises(AttributeError):
        depo.acik_sayisi = 3  # pyright: ignore[reportAttributeAccessIssue]


def test_durumdakiler():
    depo = TalepDeposu.dosyadan(ORNEK)
    kapalilar = depo.durumdakiler(Durum.KAPALI)
    assert isinstance(kapalilar, TalepDeposu)
    assert [t.id for t in kapalilar] == [2, 8]
    assert len(depo) == 12


def test_eski_fonksiyonlar_depoyla_calisir():
    depo = TalepDeposu.dosyadan(ORNEK)
    assert durum_sayilari(depo) == {"acik": 6, "beklemede": 4, "kapali": 2}
    assert [t.id for t in kapanmamislar(depo)] == [1, 3, 4, 5, 6, 7, 9, 10, 11, 12]
