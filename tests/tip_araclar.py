# pyright: strict
"""pyright bu dosyayı denetler; pytest çalıştırmaz, çünkü adı test_ ile başlamıyor."""

from typing import Any, assert_type

from yardim_masasi.araclar import yeniden_dene
from yardim_masasi.pypi import paket_bilgisi


@yeniden_dene(kez=2, hatalar=(ConnectionError,))
def kare(x: int, *, eksi: bool = False) -> int:
    return -x * x if eksi else x * x


def dogru_kullanimlar() -> None:
    assert_type(kare(3), int)
    assert_type(kare(3, eksi=True), int)
    assert_type(kare.__name__, str)
    assert_type(paket_bilgisi("httpx"), dict[str, Any])


def yanlis_kullanimlar() -> None:
    # Her satır bir tip hatası olmalı. Hata çıkmazsa pyright "gereksiz ignore" der.
    kare("3")  # pyright: ignore[reportArgumentType]
    kare(3, ters=True)  # pyright: ignore[reportCallIssue]
    kare()  # pyright: ignore[reportCallIssue]
    kare(3, True)  # pyright: ignore[reportCallIssue]
    yeniden_dene(kez="3")  # pyright: ignore[reportArgumentType]
    yeniden_dene(hatalar=(int,))  # pyright: ignore[reportArgumentType]
