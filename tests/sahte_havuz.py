"""/saglik testleri için havuz taklidi: veritabanı olmadan bağlantıyı ve hataları taklit eder."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager


class SahteBaglanti:
    def __init__(self, hata: Exception | None) -> None:
        self.hata = hata
        self.sorgular: list[str] = []

    async def execute(self, sorgu: str) -> None:
        self.sorgular.append(sorgu)
        if self.hata is not None:
            raise self.hata


class SahteHavuz:
    """AsyncConnectionPool'un connection(timeout=...) metodunu taklit eder.

    bekleme_hatasi: havuz bağlantı veremeden fırlar (ör. PoolTimeout).
    sorgu_hatasi: bağlantı alındıktan sonra execute'ta fırlar (ör. kopmuş bağlantı).
    istenen_sureler: connection'a verilen timeout değerleri, sırayla.
    """

    def __init__(self, bekleme_hatasi: Exception | None = None, sorgu_hatasi: Exception | None = None) -> None:
        self.bekleme_hatasi = bekleme_hatasi
        self.baglanti = SahteBaglanti(sorgu_hatasi)
        self.istenen_sureler: list[float | None] = []

    @asynccontextmanager
    async def connection(self, timeout: float | None = None) -> AsyncIterator[SahteBaglanti]:
        self.istenen_sureler.append(timeout)
        if self.bekleme_hatasi is not None:
            raise self.bekleme_hatasi
        yield self.baglanti
