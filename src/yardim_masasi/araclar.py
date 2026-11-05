import functools
import time
from collections.abc import Callable


def yeniden_dene(
    kez: int = 3,
    hatalar: tuple[type[Exception], ...] = (Exception,),
    bekleme: float = 0.0,
) -> Callable:
    if kez < 1:
        raise ValueError("kez en az 1 olmalı")

    def dekorator(fonk):
        @functools.wraps(fonk)
        def sarici(*args, **kwargs):
            for deneme in range(1, kez + 1):
                try:
                    return fonk(*args, **kwargs)
                except hatalar:
                    if deneme == kez:
                        raise
                    time.sleep(bekleme)
        return sarici
    return dekorator
