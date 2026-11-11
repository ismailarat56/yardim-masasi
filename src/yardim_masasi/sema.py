from datetime import datetime
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from yardim_masasi.model import Durum, Oncelik

Baslik = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=200)]
Musteri = Annotated[str, Field(pattern=r"^[^@\s]+@[^@\s]+$")]
Etiket = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=30)]


class TalepOlustur(BaseModel):
    model_config = ConfigDict(extra="forbid")

    baslik: Baslik
    musteri: Musteri
    oncelik: Oncelik = Oncelik.ORTA
    etiketler: list[Etiket] = []


class TalepGuncelle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    durum: Durum | None = None
    oncelik: Oncelik | None = None

    @model_validator(mode="after")
    def en_az_bir_alan(self) -> Self:
        if self.durum is None and self.oncelik is None:
            raise ValueError("durum ya da oncelik verilmeli")
        return self


class TalepCevap(BaseModel):
    id: int
    baslik: str
    durum: Durum
    oncelik: Oncelik
    musteri: str
    etiketler: list[str]
    acildi: datetime
    surum: int


Yazan = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=60)]
YorumMetni = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]


class YorumOlustur(BaseModel):
    model_config = ConfigDict(extra="forbid")

    yazan: Yazan
    metin: YorumMetni


class YorumCevap(BaseModel):
    id: int
    talep_id: int
    yazan: str
    metin: str
    yazildi: datetime
