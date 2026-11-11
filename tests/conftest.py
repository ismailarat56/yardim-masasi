import os
from pathlib import Path

import psycopg
import pytest
from alembic import command
from alembic.config import Config

GOCLER = Path(__file__).parent.parent / "migrations"


@pytest.fixture
def anyio_backend():
    return "asyncio"


def alembic_ayari(adres: str) -> Config:
    """alembic.ini'yi okumadan, testin veritabanına bakan bir Alembic ayarı kurar."""
    ayar = Config()
    ayar.set_main_option("script_location", str(GOCLER))
    ayar.set_main_option("sqlalchemy.url", adres)
    return ayar


@pytest.fixture(scope="session")
def test_adresi() -> str:
    """Test veritabanını boşaltır ve şemayı migration'larla baştan kurar. Oturumda bir kez çalışır."""
    adres = os.environ.get("TEST_DATABASE_URL")
    if not adres:
        pytest.skip("TEST_DATABASE_URL tanımlı değil")
    with psycopg.connect(adres) as baglanti:
        baglanti.execute("DROP SCHEMA public CASCADE")
        baglanti.execute("CREATE SCHEMA public")
    command.upgrade(alembic_ayari(adres), "head")
    return adres
