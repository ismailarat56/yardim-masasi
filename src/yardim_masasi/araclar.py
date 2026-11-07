# pyright: strict
import functools
import logging
import time
from collections.abc import Callable

log = logging.getLogger(__name__)


def yeniden_dene[**P, R](
    kez: int = 3,
    hatalar: tuple[type[Exception], ...] = (Exception,),
    bekleme: float = 0.0,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    if kez < 1:
        raise ValueError("kez en az 1 olmalı")

    def dekorator(fonk: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(fonk)
        def sarici(*args: P.args, **kwargs: P.kwargs) -> R:
            for deneme in range(1, kez + 1):
                try:
                    return fonk(*args, **kwargs)
                except hatalar as hata:
                    if deneme == kez:
                        log.error(
                            "%s: deneme %d/%d başarısız (%s), deneme hakkı bitti",
                            fonk.__name__, deneme, kez, type(hata).__name__,
                        )
                        raise
                    log.warning(
                        "%s: deneme %d/%d başarısız (%s), %.1f sn sonra yeniden",
                        fonk.__name__, deneme, kez, type(hata).__name__, bekleme,
                    )
                    time.sleep(bekleme)
            raise AssertionError("buraya hiç gelinmez")
        return sarici
    return dekorator
