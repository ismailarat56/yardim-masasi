import functools
import json
import runpy

import httpx
import pytest

from yardim_masasi import main

GERCEK_ISTEMCI = httpx.AsyncClient


@pytest.fixture
def sahte_pypi(monkeypatch):
    """httpx.AsyncClient'ı sahte PyPI'a bağlar. Dönen sözlüğe {"paket": 404} yazarak durum kodu verebilirsin."""
    durumlar = {}

    def yanitla(istek):
        paket = istek.url.path.split("/")[2]
        govde = {"info": {"name": paket, "version": "1.0", "requires_python": ">=3.10"}}
        return httpx.Response(durumlar.get(paket, 200), content=json.dumps(govde))

    istemci = functools.partial(GERCEK_ISTEMCI, transport=httpx.MockTransport(yanitla))
    monkeypatch.setattr(httpx, "AsyncClient", istemci)
    return durumlar


def test_ozetleri_paket_sirasiyla_yazar(sahte_pypi, capsys):
    assert main(["httpx", "rich"]) == 0
    cikti = capsys.readouterr()
    assert cikti.out == "httpx 1.0 (Python >=3.10)\nrich 1.0 (Python >=3.10)\n"
    assert cikti.err == ""


def test_paket_verilmezse_kullanim_hatasi(capsys):
    with pytest.raises(SystemExit) as bilgi:
        main([])
    assert bilgi.value.code == 2
    assert "PAKET" in capsys.readouterr().err


def test_bulunamayan_paket_diger_ozetleri_engellemez(sahte_pypi, capsys):
    sahte_pypi["yok"] = 404
    assert main(["httpx", "yok", "rich"]) == 1
    cikti = capsys.readouterr()
    assert cikti.out == "httpx 1.0 (Python >=3.10)\nrich 1.0 (Python >=3.10)\n"
    assert cikti.err == "yardim-masasi: yok: PyPI 404 döndü\n"


def test_sunucu_hatasi_paket_hatasi_sayilir(sahte_pypi, capsys):
    sahte_pypi["bozuk"] = 500
    assert main(["bozuk"]) == 1
    cikti = capsys.readouterr()
    assert cikti.out == ""
    assert cikti.err == "yardim-masasi: bozuk: PyPI 500 döndü\n"


@pytest.mark.parametrize("deger", ["0", "-2", "abc"])
def test_gecersiz_eszamanlilik_kullanim_hatasi(deger, sahte_pypi, capsys):
    with pytest.raises(SystemExit) as bilgi:
        main(["-e", deger, "httpx"])
    assert bilgi.value.code == 2
    cikti = capsys.readouterr()
    assert "--eszamanli" in cikti.err
    assert cikti.out == ""


def test_uzun_eszamanli_bayragi_iki_paketi_yazar(sahte_pypi, capsys):
    assert main(["--eszamanli", "1", "httpx", "rich"]) == 0
    cikti = capsys.readouterr()
    assert cikti.out == "httpx 1.0 (Python >=3.10)\nrich 1.0 (Python >=3.10)\n"
    assert cikti.err == ""


def test_baglanti_hatasi_kod_1_ile_biter(monkeypatch, capsys):
    def koptu(istek):
        raise httpx.ConnectError("bağlanamadı", request=istek)

    async def hemen(saniye):
        pass

    istemci = functools.partial(GERCEK_ISTEMCI, transport=httpx.MockTransport(koptu))
    monkeypatch.setattr(httpx, "AsyncClient", istemci)
    monkeypatch.setattr("asyncio.sleep", hemen)
    with pytest.raises(SystemExit) as bilgi:
        main(["httpx"])
    assert bilgi.value.code == 1
    cikti = capsys.readouterr()
    assert cikti.out == ""
    assert cikti.err.endswith("yardim-masasi: PyPI'a ulaşılamadı: bağlanamadı\n")
    assert "Traceback" not in cikti.err


def test_help_eszamanli_bayragini_gosterir(capsys):
    with pytest.raises(SystemExit) as bilgi:
        main(["--help"])
    assert bilgi.value.code == 0
    cikti = capsys.readouterr()
    assert "--eszamanli" in cikti.out
    assert cikti.err == ""


@pytest.mark.parametrize(("durum", "kod"), [(200, 0), (404, 1)])
def test_modul_girisi_main_cikis_kodunu_kullanir(sahte_pypi, monkeypatch, capsys, durum, kod):
    sahte_pypi["httpx"] = durum
    monkeypatch.setattr("sys.argv", ["yardim_masasi", "httpx"])
    with pytest.raises(SystemExit) as bilgi:
        runpy.run_module("yardim_masasi.__main__", run_name="__main__")
    assert bilgi.value.code == kod
    cikti = capsys.readouterr()
    if durum == 200:
        assert cikti.out == "httpx 1.0 (Python >=3.10)\n"
        assert cikti.err == ""
    else:
        assert cikti.out == ""
        assert cikti.err == "yardim-masasi: httpx: PyPI 404 döndü\n"
