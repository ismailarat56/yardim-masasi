import asyncio
import json

import httpx
import pytest

from yardim_masasi.pypi import paketleri_getir


class SahtePyPI:
    """httpx.MockTransport ile çalışan sahte PyPI: her paket için gecikme ve durum kodu verilebilir."""

    def __init__(self, gecikmeler=None, durumlar=None, kopmalar=0):
        self.gecikmeler = gecikmeler or {}
        self.durumlar = durumlar or {}
        self.kopmalar = kopmalar
        self.istekler = []
        self.simdi = 0
        self.en_cok = 0

    async def __call__(self, istek):
        paket = istek.url.path.split("/")[2]
        self.istekler.append(paket)
        if self.kopmalar:
            self.kopmalar -= 1
            raise httpx.ConnectError("bağlantı koptu", request=istek)
        self.simdi += 1
        self.en_cok = max(self.en_cok, self.simdi)
        try:
            await asyncio.sleep(self.gecikmeler.get(paket, 0.02))
        finally:
            self.simdi -= 1
        durum = self.durumlar.get(paket, 200)
        govde = {"info": {"name": paket, "version": "1.0", "requires_python": ">=3.10"}}
        return httpx.Response(durum, content=json.dumps(govde))

    def istemci(self):
        return httpx.AsyncClient(transport=httpx.MockTransport(self))


def getir(sahte, paketler, en_fazla=4):
    async def calistir():
        async with sahte.istemci() as istemci:
            return await paketleri_getir(paketler, en_fazla=en_fazla, istemci=istemci)

    return asyncio.run(calistir())


def adlar(sonuclar):
    return [s["info"]["name"] for s in sonuclar]


def test_sonuclar_paket_sirasiyla_doner():
    sahte = SahtePyPI(gecikmeler={"a": 0.06, "b": 0.01, "c": 0.03})
    assert adlar(getir(sahte, ["a", "b", "c"])) == ["a", "b", "c"]


def test_her_paket_bir_kez_istenir():
    sahte = SahtePyPI()
    getir(sahte, ["a", "b", "c", "d"])
    assert sorted(sahte.istekler) == ["a", "b", "c", "d"]


def test_ayni_anda_en_fazla_n_istek():
    sahte = SahtePyPI()
    getir(sahte, [f"p{i}" for i in range(9)], en_fazla=3)
    assert sahte.en_cok == 3


def test_bulunamayan_paket_sonuc_olarak_doner_ve_denenmez():
    sahte = SahtePyPI(durumlar={"yok": 404})
    sonuclar = getir(sahte, ["a", "yok", "b"])
    assert adlar([sonuclar[0], sonuclar[2]]) == ["a", "b"]
    assert isinstance(sonuclar[1], httpx.HTTPStatusError)
    assert sonuclar[1].response.status_code == 404
    assert sahte.istekler.count("yok") == 1


def test_kopan_baglanti_yeniden_denenir():
    sahte = SahtePyPI(kopmalar=1)
    assert adlar(getir(sahte, ["a"])) == ["a"]
    assert sahte.istekler == ["a", "a"]


def test_hep_kopan_baglanti_hata_grubu_olur():
    sahte = SahtePyPI(kopmalar=10)
    with pytest.raises(ExceptionGroup) as bilgi:
        getir(sahte, ["a"])
    assert bilgi.group_contains(httpx.ConnectError)
    assert sahte.istekler == ["a", "a", "a"]
