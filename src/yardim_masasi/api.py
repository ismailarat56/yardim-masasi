import os
import re
import secrets
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Path, Query, Request, Response
from psycopg import OperationalError
from psycopg_pool import AsyncConnectionPool

from yardim_masasi.model import Durum, Oncelik, SurumCakismasi, Talep, Yorum
from yardim_masasi.pg_depo import PgTalepDeposu
from yardim_masasi.sayfa import Ayrac, GecersizAyrac, ayrac_oku, ayrac_yaz
from yardim_masasi.sema import TalepCevap, TalepGuncelle, TalepOlustur, TalepSayfasi, YorumCevap, YorumOlustur
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


SURUM_ETIKETI = re.compile(r'"([1-9][0-9]*)"')


def etag(talep: Talep) -> str:
    return f'"{talep.surum}"'


def etiket_uyar(if_none_match: str, guncel: str) -> bool:
    """If-None-Match zayıf karşılaştırılır: W/"3" ile "3" aynıdır; * her etikete uyar."""
    if if_none_match.strip() == "*":
        return True
    return any(parca.strip().removeprefix("W/") == guncel for parca in if_none_match.split(","))


def beklenen_surum(if_match: Annotated[str | None, Header()] = None) -> int:
    if if_match is None:
        raise HTTPException(status_code=428, detail="If-Match başlığı gerekli: önce talebi GET ile oku")
    eslesme = SURUM_ETIKETI.fullmatch(if_match.strip())
    if eslesme is None:
        raise HTTPException(status_code=400, detail='If-Match tırnaklı bir sürüm olmalı, örneğin "3"')
    return int(eslesme.group(1))


def sayfa_ayraci(ayrac: Annotated[str | None, Query()] = None) -> Ayrac | None:
    if ayrac is None:
        return None
    try:
        return ayrac_oku(ayrac)
    except GecersizAyrac as hata:
        raise HTTPException(
            status_code=400,
            detail="ayraç geçersiz: önceki sayfanın sonraki alanını değiştirmeden gönder",
        ) from hata


Depo = Annotated[PgTalepDeposu, Depends(depo_al)]
TalepNo = Annotated[int, Path(gt=0)]
BeklenenSurum = Annotated[int, Depends(beklenen_surum)]
SayfaAyraci = Annotated[Ayrac | None, Depends(sayfa_ayraci)]
Limit = Annotated[int, Query(ge=1, le=100)]
Arama = Annotated[str | None, Query(min_length=2, max_length=100)]


SAGLIK_SURESI = 2


@app.get("/saglik")
async def saglik(request: Request, response: Response) -> dict[str, str]:
    """Veritabanına SAGLIK_SURESI saniyede ulaşamazsa 503 döner.

    Havuz kendi başına 30 saniye bekler; sağlık kontrolü o kadar bekleyemez.
    PoolTimeout da kopmuş bağlantının hatası da OperationalError'dır.
    """
    try:
        async with request.app.state.havuz.connection(timeout=SAGLIK_SURESI) as baglanti:
            await baglanti.execute("SELECT 1")
    except OperationalError:
        response.status_code = 503
        return {"durum": "veritabanına ulaşılamıyor"}
    return {"durum": "ok"}


@app.get("/talepler", response_model=TalepSayfasi)
async def talepleri_listele(
    depo: Depo,
    sonra: SayfaAyraci,
    durum: Durum | None = None,
    oncelik: Oncelik | None = None,
    etiket: str | None = None,
    ara: Arama = None,
    limit: Limit = 20,
) -> dict[str, object]:
    sayfa = await depo.listele(durum=durum, oncelik=oncelik, etiket=etiket, ara=ara, sonra=sonra, limit=limit)
    return {
        "talepler": sayfa.talepler,
        "sonraki": None if sayfa.sonraki is None else ayrac_yaz(sayfa.sonraki),
    }


@app.get("/talepler/ozet")
async def talep_ozeti(depo: Depo) -> dict[Durum, int]:
    return await depo.durum_sayilari()


@app.get("/talepler/{talep_id}", response_model=TalepCevap)
async def talep_getir(
    talep_id: TalepNo,
    depo: Depo,
    response: Response,
    if_none_match: Annotated[str | None, Header()] = None,
) -> Talep | Response:
    talep = await depo.getir(talep_id)
    if talep is None:
        raise HTTPException(status_code=404, detail="talep bulunamadı")
    if if_none_match is not None and etiket_uyar(if_none_match, etag(talep)):
        return Response(status_code=304, headers={"ETag": etag(talep)})
    response.headers["ETag"] = etag(talep)
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
async def talep_guncelle(
    talep_id: TalepNo,
    govde: TalepGuncelle,
    surum: BeklenenSurum,
    depo: Depo,
    response: Response,
) -> Talep:
    try:
        talep = await depo.guncelle(talep_id, surum=surum, durum=govde.durum, oncelik=govde.oncelik)
    except SurumCakismasi as hata:
        raise HTTPException(
            status_code=412,
            detail="talep sen okuduktan sonra değişti",
            headers={"ETag": etag(hata.guncel)},
        ) from hata
    if talep is None:
        raise HTTPException(status_code=404, detail="talep bulunamadı")
    response.headers["ETag"] = etag(talep)
    return talep


@app.get("/talepler/{talep_id}/yorumlar", response_model=list[YorumCevap])
async def yorumlari_listele(talep_id: TalepNo, depo: Depo) -> list[Yorum]:
    yorumlar = await depo.yorumlar(talep_id)
    if yorumlar is None:
        raise HTTPException(status_code=404, detail="talep bulunamadı")
    return yorumlar


@app.post(
    "/talepler/{talep_id}/yorumlar",
    status_code=201,
    response_model=YorumCevap,
    dependencies=[Depends(anahtar_gerekli)],
)
async def yorum_ekle(talep_id: TalepNo, govde: YorumOlustur, depo: Depo) -> Yorum:
    yorum = await depo.yorum_ekle(talep_id, yazan=govde.yazan, metin=govde.metin)
    if yorum is None:
        raise HTTPException(status_code=404, detail="talep bulunamadı")
    return yorum
