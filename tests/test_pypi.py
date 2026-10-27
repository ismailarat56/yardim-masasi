from yardim_masasi.pypi import ozet, zaman_asimi


def test_ozet_ad_surum_ve_python_yazar():
    veri = {"info": {"name": "httpx", "version": "0.28.1", "requires_python": ">=3.8"}}
    assert ozet(veri) == "httpx 0.28.1 (Python >=3.8)"


def test_python_yoksa_belirtilmemis_yazar():
    veri = {"info": {"name": "eski", "version": "1.0", "requires_python": None}}
    assert ozet(veri) == "eski 1.0 (Python belirtilmemiş)"


def test_python_bos_metinse_belirtilmemis_yazar():
    veri = {"info": {"name": "eski", "version": "1.0", "requires_python": ""}}
    assert ozet(veri) == "eski 1.0 (Python belirtilmemiş)"


def test_zaman_asimi_varsayilan_on_saniye(monkeypatch):
    monkeypatch.delenv("PYPI_ZAMAN_ASIMI", raising=False)
    assert zaman_asimi() == 10.0


def test_zaman_asimi_ortamdan_okunur(monkeypatch):
    monkeypatch.setenv("PYPI_ZAMAN_ASIMI", "2.5")
    assert zaman_asimi() == 2.5
