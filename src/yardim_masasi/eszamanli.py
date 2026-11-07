# pyright: strict
import asyncio
import functools
import logging
from collections.abc import Awaitable, Callable, Coroutine, Iterable
from typing import Any

log = logging.getLogger(__name__)


async def sinirli_topla[T](
    isler: Iterable[Callable[[], Awaitable[T]]],
    *,
    en_fazla: int,
) -> list[T]:
    if en_fazla < 1:
        raise ValueError("en_fazla en az 1 olmalı")

    sinir = asyncio.Semaphore(en_fazla)

    async def sirayla_bekle(is_: Callable[[], Awaitable[T]]) -> T:
        async with sinir:
            return await is_()

    async with asyncio.TaskGroup() as grup:
        gorevler = [grup.create_task(sirayla_bekle(is_)) for is_ in isler]

    return [gorev.result() for gorev in gorevler]


def yeniden_dene_async[**P, R](
    kez: int = 3,
    hatalar: tuple[type[Exception], ...] = (Exception,),
    bekleme: float = 0.0,
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Coroutine[Any, Any, R]]]:
    if kez < 1:
        raise ValueError("kez en az 1 olmalı")

    def dekorator(
        fonk: Callable[P, Awaitable[R]],
    ) -> Callable[P, Coroutine[Any, Any, R]]:
        @functools.wraps(fonk)
        async def sarici(*args: P.args, **kwargs: P.kwargs) -> R:
            for deneme in range(1, kez + 1):
                try:
                    return await fonk(*args, **kwargs)
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
                    await asyncio.sleep(bekleme)
            raise AssertionError("buraya hiç gelinmez")
        return sarici
    return dekorator
