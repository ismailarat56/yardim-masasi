import json

import pytest

from yardim_masasi.akis import JsonSatirHatasi, jsonl_oku, parcalara_bol, satirlari_oku


def dosya(tmp_path, metin, ad="veri.txt"):
    yol = tmp_path / ad
    yol.write_text(metin, encoding="utf-8")
    return yol


def test_satirlar_numarasiyla_gelir(tmp_path):
    yol = dosya(tmp_path, "birinci\nikinci\nüçüncü\n")
    assert list(satirlari_oku(yol)) == [(1, "birinci"), (2, "ikinci"), (3, "üçüncü")]


def test_bos_satirlar_atlanir_numara_korunur(tmp_path):
    yol = dosya(tmp_path, "a\n\n   \nb\n")
    assert list(satirlari_oku(yol)) == [(1, "a"), (4, "b")]


def test_bastaki_ve_sondaki_bosluklar_kirpilir(tmp_path):
    yol = dosya(tmp_path, "  a  \n   b\n")
    assert list(satirlari_oku(yol)) == [(1, "a"), (2, "b")]


def test_son_satirda_satir_sonu_olmayabilir(tmp_path):
    yol = dosya(tmp_path, "a\nb")
    assert list(satirlari_oku(yol)) == [(1, "a"), (2, "b")]


def test_bos_dosya(tmp_path):
    assert list(satirlari_oku(dosya(tmp_path, ""))) == []


def test_satirlari_oku_tembeldir(tmp_path):
    uretec = satirlari_oku(tmp_path / "yok.txt")
    with pytest.raises(FileNotFoundError):
        next(uretec)


def test_jsonl_her_satiri_cozer(tmp_path):
    yol = dosya(tmp_path, '{"id": 1}\n\n[1, 2]\n"metin"\n', "veri.jsonl")
    assert list(jsonl_oku(yol)) == [{"id": 1}, [1, 2], "metin"]


def test_jsonl_bozuk_satir(tmp_path):
    yol = dosya(tmp_path, '{"id": 1}\n\n{"id": }\n', "veri.jsonl")
    with pytest.raises(JsonSatirHatasi) as bilgi:
        list(jsonl_oku(yol))
    assert bilgi.value.satir == 3
    assert bilgi.value.sutun == 8
    assert str(bilgi.value) == "3. satır geçerli JSON değil (sütun 8)"
    assert isinstance(bilgi.value.__cause__, json.JSONDecodeError)


def test_jsonl_bozuk_satira_kadar_verir(tmp_path):
    yol = dosya(tmp_path, '{"id": 1}\nbozuk\n{"id": 3}\n', "veri.jsonl")
    uretec = jsonl_oku(yol)
    assert next(uretec) == {"id": 1}
    with pytest.raises(JsonSatirHatasi):
        next(uretec)


def test_parcalar():
    assert list(parcalara_bol(range(5), 2)) == [[0, 1], [2, 3], [4]]


def test_tam_bolunen_parcalar():
    assert list(parcalara_bol("abcdef", 3)) == [["a", "b", "c"], ["d", "e", "f"]]
    assert list(parcalara_bol([7, 8], 1)) == [[7], [8]]


def test_bos_giris():
    assert list(parcalara_bol([], 3)) == []


def test_uretecle_calisir():
    kareler = (sayi * sayi for sayi in range(3))
    assert list(parcalara_bol(kareler, 2)) == [[0, 1], [4]]


def test_yalniz_gerektigi_kadar_okur():
    okunan = []

    def kaynak():
        for sayi in range(1000):
            okunan.append(sayi)
            yield sayi

    ilk = next(parcalara_bol(kaynak(), 3))
    assert ilk == [0, 1, 2]
    assert okunan == [0, 1, 2]


def test_gecersiz_boyut_hemen_reddedilir():
    with pytest.raises(ValueError, match="boyut en az 1 olmalı"):
        parcalara_bol([1, 2], 0)
