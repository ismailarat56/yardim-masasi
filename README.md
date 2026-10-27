# Yardım Masası

`yardim-masasi` komutu küçük bir araç: verdiğin paketlerin PyPI'daki en yeni sürümünü ve istediği Python aralığını yazar.

## Gerekenler

- uv: https://docs.astral.sh/uv/
- Python 3.15: `.python-version` dosyasında yazılı; uv kendisi kurar. Sistemdeki `python3` kullanılmaz.

## Kurulum

    uv sync

`uv.lock`'taki sürümlerin aynısını `.venv` klasörüne kurar. `.venv` git'e girmez; silersen `uv sync` yeniden kurar.

## Çalıştırma

    uv run yardim-masasi httpx fastapi

## Ortam Değişkenleri

`.env.example` dosyasını `.env` olarak kopyala. `.env` git'e girmez.

    PYPI_ZAMAN_ASIMI   PyPI isteğinin zaman aşımı, saniye (varsayılan 10)

uv `.env`'i kendiliğinden okumaz:

    uv run --env-file .env yardim-masasi httpx

## Testler

    uv run pytest

## Paketler

    uv add paket             çalışma bağımlılığı (pyproject.toml + uv.lock)
    uv add --dev paket       yalnız geliştirmede (dependency-groups.dev)
    uv remove paket
    uv tree --outdated       yeni sürümü çıkmış paketler
    uv lock --upgrade-package paket   tek paketi, izin verilen aralıkta yükselt

## Bilinen Sınırlamalar

- Paket bulunamazsa ya da istek zaman aşımına uğrarsa düzgün bir mesaj yok; Python'un hata izi basılır.
- `PYPI_ZAMAN_ASIMI` sayı değilse program `ValueError` ile durur.
- Bağımlılıklar güvenlik açığı için taranmıyor.
