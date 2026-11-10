import os
import secrets
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Path, Request
from psycopg_pool import AsyncConnectionPool

from yardim_masasi.model import Durum, Oncelik, Talep
from yardim_masasi.pg_depo import PgTalepDeposu
from yardim_masasi.sema import TalepCevap, TalepGuncelle, TalepOlustur
from yardim_masasi.veritabani import baglanti_adresi


@asynccontextmanager
async def omur(app: FastAPI) -> AsyncIterator[None]:
    havuz = AsyncConnectionPool(baglanti_adresi(), min_size=1, max_size=5, open=False)
    await havuz.open(wait=True, timeout=5)
    app.state.havuz = havuz
    try:
        yield
    finally:
        await havuz.close()


app = FastAPI(title="Yardım Masası", lifespan=omur)


def depo_al(request: Request) -> PgTalepDeposu:
    return PgTalepDeposu(request.app.state.havuz)


def anahtar_gerekli(x_api_anahtari: Annotated[str | None, Header()] = None) -> None:
    beklenen = os.environ.get("API_ANAHTARI")
    if not beklenen or x_api_anahtari is None:
        raise HTTPException(status_code=401, detail="geçerli bir API anahtarı gerekli")
    if not secrets.compare_digest(x_api_anahtari.encode(), beklenen.encode()):
        raise HTTPException(status_code=401, detail="geçerli bir API anahtarı gerekli")


Depo = Annotated[PgTalepDeposu, Depends(depo_al)]
TalepNo = Annotated[int, Path(gt=0)]


@app.get("/saglik")
async def saglik(request: Request) -> dict[str, str]:
    async with request.app.state.havuz.connection() as baglanti:
        await baglanti.execute("SELECT 1")
    return {"durum": "ok"}


@app.get("/talepler", response_model=list[TalepCevap])
async def talepleri_listele(
    depo: Depo,
    durum: Durum | None = None,
    oncelik: Oncelik | None = None,
    etiket: str | None = None,
) -> list[Talep]:
    return await depo.listele(durum=durum, oncelik=oncelik, etiket=etiket)


@app.get("/talepler/ozet")
async def talep_ozeti(depo: Depo) -> dict[Durum, int]:
    return await depo.durum_sayilari()


@app.get("/talepler/{talep_id}", response_model=TalepCevap)
async def talep_getir(talep_id: TalepNo, depo: Depo) -> Talep:
    talep = await depo.getir(talep_id)
    if talep is None:
        raise HTTPException(status_code=404, detail="talep bulunamadı")
    return talep


@app.post(
    "/talepler",
    status_code=201,
    response_model=TalepCevap,
    dependencies=[Depends(anahtar_gerekli)],
)
async def talep_olustur(govde: TalepOlustur, depo: Depo) -> Talep:
    return await depo.ekle(**govde.model_dump())


@app.patch(
    "/talepler/{talep_id}",
    response_model=TalepCevap,
    dependencies=[Depends(anahtar_gerekli)],
)
async def talep_guncelle(talep_id: TalepNo, govde: TalepGuncelle, depo: Depo) -> Talep:
    talep = await depo.guncelle(talep_id, durum=govde.durum, oncelik=govde.oncelik)
    if talep is None:
        raise HTTPException(status_code=404, detail="talep bulunamadı")
    return talep
