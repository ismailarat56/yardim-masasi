import json

import pytest

from yardim_masasi.talepler import main

TALEP = {"id": 1, "baslik": "Giriş yapamıyorum", "durum": "acik", "oncelik": "yuksek", "musteri": "ayse@example.com"}


def calistir(monkeypatch, *argumanlar):
    monkeypatch.setattr("sys.argv", ["talep-ozeti", *argumanlar])
    main()


def dosya(tmp_path, veri):
    yol = tmp_path / "talepler.json"
    yol.write_text(json.dumps(veri), encoding="utf-8")
    return yol


def test_gecerli_dosyanin_ozetini_yazar(tmp_path, monkeypatch, capsys):
    calistir(monkeypatch, str(dosya(tmp_path, [TALEP])))
    cikti = capsys.readouterr()
    assert cikti.out == "acik: 1, beklemede: 0, kapali: 0\n\n#  1 yuksek acik      Giriş yapamıyorum\n"
    assert cikti.err == ""


def test_olmayan_dosya_kod_1_ile_biter(tmp_path, monkeypatch, capsys):
    yol = tmp_path / "yok.json"
    with pytest.raises(SystemExit) as bilgi:
        calistir(monkeypatch, str(yol))
    assert bilgi.value.code == 1
    cikti = capsys.readouterr()
    assert cikti.out == ""
    assert cikti.err == f"talep-ozeti: dosya bulunamadı: {yol}\n"


def test_gecersiz_talep_kod_1_ile_biter(tmp_path, monkeypatch, capsys):
    yol = dosya(tmp_path, [{**TALEP, "oncelik": "acil"}])
    with pytest.raises(SystemExit) as bilgi:
        calistir(monkeypatch, str(yol))
    assert bilgi.value.code == 1
    assert capsys.readouterr().err == "talep-ozeti: 1. talep: bilinmeyen öncelik: 'acil'\n"


def test_fazla_arguman_kod_2_ile_biter(monkeypatch, capsys):
    with pytest.raises(SystemExit) as bilgi:
        calistir(monkeypatch, "a.json", "b.json")
    assert bilgi.value.code == 2
    assert capsys.readouterr().err == "kullanım: talep-ozeti [dosya]\n"
