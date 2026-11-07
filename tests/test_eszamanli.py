import asyncio
import logging
import time

import pytest

from yardim_masasi.eszamanli import sinirli_topla, yeniden_dene_async


def calistir(coro, sure=2):
    """Coroutine'i en fazla sure saniye çalıştırır; hatalı bir çözüm testi sonsuza kadar asmasın."""

    async def sinirli():
        async with asyncio.timeout(sure):
            return await coro

    return asyncio.run(sinirli())


def gecikmeli(deger, saniye, olaylar=None):
    """saniye kadar bekleyip deger döndüren bir iş üretir; olaylar listesine başladı/bitti yazar."""

    async def is_():
        if olaylar is not None:
            olaylar.append(f"{deger} başladı")
        await asyncio.sleep(saniye)
        if olaylar is not None:
            olaylar.append(f"{deger} bitti")
        return deger

    return is_


class Sayac:
    """Aynı anda kaç işin çalıştığını sayar."""

    def __init__(self):
        self.simdi = 0
        self.en_cok = 0

    def is_(self, deger, saniye=0.02):
        async def is_():
            self.simdi += 1
            self.en_cok = max(self.en_cok, self.simdi)
            try:
                await asyncio.sleep(saniye)
            finally:
                self.simdi -= 1
            return deger

        return is_


# sinirli_topla


def test_sonuclar_girdi_sirasiyla_doner():
    isler = [gecikmeli("a", 0.06), gecikmeli("b", 0.02), gecikmeli("c", 0.04)]
    assert calistir(sinirli_topla(isler, en_fazla=3)) == ["a", "b", "c"]


def test_bos_girdi_bos_liste():
    assert calistir(sinirli_topla([], en_fazla=2)) == []


def test_ayni_anda_en_fazla_n_is_calisir():
    sayac = Sayac()
    isler = [sayac.is_(sira) for sira in range(7)]
    assert calistir(sinirli_topla(isler, en_fazla=3)) == list(range(7))
    assert sayac.en_cok == 3


def test_sinir_yetiyorsa_hepsi_birlikte_calisir():
    sayac = Sayac()
    isler = [sayac.is_(sira, saniye=0.1) for sira in range(4)]
    baslangic = time.perf_counter()
    calistir(sinirli_topla(isler, en_fazla=10))
    assert sayac.en_cok == 4
    assert time.perf_counter() - baslangic < 0.3


def test_en_fazla_bir_ise_sirayla_calisir():
    olaylar = []
    isler = [gecikmeli("a", 0.02, olaylar), gecikmeli("b", 0.01, olaylar)]
    calistir(sinirli_topla(isler, en_fazla=1))
    assert olaylar == ["a başladı", "a bitti", "b başladı", "b bitti"]


def test_isler_ureteçten_gelebilir():
    isler = (gecikmeli(sira, 0.01) for sira in range(3))
    assert calistir(sinirli_topla(isler, en_fazla=2)) == [0, 1, 2]


@pytest.mark.parametrize("en_fazla", [0, -1])
def test_en_fazla_birden_kucukse_hata(en_fazla):
    with pytest.raises(ValueError, match="en_fazla"):
        calistir(sinirli_topla([gecikmeli("a", 0)], en_fazla=en_fazla))


def test_bir_is_hata_verirse_hata_grubu_yukselir_ve_digerleri_iptal_edilir():
    olaylar = []

    async def bozuk():
        await asyncio.sleep(0.02)
        raise ValueError("bozuldu")

    isler = [gecikmeli("uzun", 1, olaylar), bozuk]
    baslangic = time.perf_counter()
    with pytest.raises(ExceptionGroup) as bilgi:
        calistir(sinirli_topla(isler, en_fazla=2))
    assert bilgi.group_contains(ValueError, match="bozuldu")
    assert olaylar == ["uzun başladı"]
    assert time.perf_counter() - baslangic < 0.5


def test_hata_sonrasi_kalan_isler_bitirilmez():
    olaylar = []

    async def bozuk():
        await asyncio.sleep(0.02)
        raise ValueError("ikinci iş bozuk")

    isler = [gecikmeli(0, 0.05, olaylar), bozuk] + [gecikmeli(sira, 0.05, olaylar) for sira in range(2, 10)]
    baslangic = time.perf_counter()
    with pytest.raises(ExceptionGroup):
        calistir(sinirli_topla(isler, en_fazla=2))
    assert not any(olay.endswith("bitti") for olay in olaylar)
    assert len(olaylar) < 5
    assert time.perf_counter() - baslangic < 0.2


# yeniden_dene_async


def bozuk_sonra_saglam(kac_kez, hata: type[Exception] = ConnectionError):
    """İlk kac_kez çağrıda hata veren, sonra "tamam" döndüren bir async fonksiyon ve çağrı listesi."""
    cagrilar = []

    async def fonk(x):
        cagrilar.append(x)
        if len(cagrilar) <= kac_kez:
            raise hata(f"{len(cagrilar)}. hata")
        return "tamam"

    return fonk, cagrilar


def test_async_ilk_denemede_basarili():
    fonk, cagrilar = bozuk_sonra_saglam(0)
    sarili = yeniden_dene_async(kez=3)(fonk)
    assert calistir(sarili(5)) == "tamam"
    assert cagrilar == [5]


def test_async_iki_hatadan_sonra_basarili():
    fonk, cagrilar = bozuk_sonra_saglam(2)
    sarili = yeniden_dene_async(kez=3, hatalar=(ConnectionError,))(fonk)
    assert calistir(sarili(5)) == "tamam"
    assert cagrilar == [5, 5, 5]


def test_async_son_deneme_de_bozuksa_hata_yukselir():
    fonk, cagrilar = bozuk_sonra_saglam(5)
    sarili = yeniden_dene_async(kez=3, hatalar=(ConnectionError,))(fonk)
    with pytest.raises(ConnectionError, match="3. hata"):
        calistir(sarili(5))
    assert len(cagrilar) == 3


def test_async_listede_olmayan_hata_denenmez():
    fonk, cagrilar = bozuk_sonra_saglam(1, hata=KeyError)
    sarili = yeniden_dene_async(kez=3, hatalar=(ConnectionError,))(fonk)
    with pytest.raises(KeyError):
        calistir(sarili(5))
    assert len(cagrilar) == 1


def test_async_kez_sifirsa_hemen_hata():
    with pytest.raises(ValueError, match="kez"):
        yeniden_dene_async(kez=0)


def test_async_sarici_async_ve_adi_korunur():
    async def paket_getir():
        return 1

    sarili = yeniden_dene_async()(paket_getir)
    assert sarili.__name__ == "paket_getir"
    sonuc = sarili()
    assert asyncio.iscoroutine(sonuc)
    assert calistir(sonuc) == 1


def test_async_beklerken_dongu_kilitlenmez():
    tikler = []
    gorulen = []

    async def iki_kez_bozuk():
        gorulen.append(len(tikler))
        if len(gorulen) <= 2:
            raise ConnectionError("koptu")
        return "tamam"

    sarili = yeniden_dene_async(kez=3, bekleme=0.05)(iki_kez_bozuk)

    async def tikla():
        for _ in range(30):
            tikler.append(1)
            await asyncio.sleep(0.01)

    async def ikisi():
        return await asyncio.gather(sarili(), tikla())

    assert calistir(ikisi())[0] == "tamam"
    # Her bekleme sırasında öbür görev en az üç kez ilerlemiş olmalı.
    assert gorulen[1] - gorulen[0] >= 3
    assert gorulen[2] - gorulen[1] >= 3


def test_async_iptal_yeniden_denenmez():
    cagrilar = []

    async def yavas():
        cagrilar.append(1)
        await asyncio.sleep(1)

    sarili = yeniden_dene_async(kez=3, hatalar=(Exception,))(yavas)

    async def sinirli():
        async with asyncio.timeout(0.05):
            await sarili()

    baslangic = time.perf_counter()
    with pytest.raises(TimeoutError):
        calistir(sinirli())
    assert cagrilar == [1]
    assert time.perf_counter() - baslangic < 0.5


def test_async_basarisiz_denemeler_gunluge_yazilir(caplog):
    fonk, _ = bozuk_sonra_saglam(5)
    sarili = yeniden_dene_async(kez=2, hatalar=(ConnectionError,))(fonk)
    with caplog.at_level(logging.DEBUG, logger="yardim_masasi"):
        with pytest.raises(ConnectionError):
            calistir(sarili(1))
    kayitlar = [(k.name, k.levelname) for k in caplog.records]
    assert kayitlar == [
        ("yardim_masasi.eszamanli", "WARNING"),
        ("yardim_masasi.eszamanli", "ERROR"),
    ]
