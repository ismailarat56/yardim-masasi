"""Migration zinciri: her adım uygulanır, geri alınır ve yeniden uygulanır."""

import psycopg
from alembic import command
from alembic.script import ScriptDirectory

from conftest import alembic_ayari


def tablolar(adres: str) -> list[str]:
    with psycopg.connect(adres) as baglanti:
        satirlar = baglanti.execute(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"
        ).fetchall()
    return [satir[0] for satir in satirlar]


def veritabanindaki_surum(adres: str) -> list[str]:
    with psycopg.connect(adres) as baglanti:
        return [satir[0] for satir in baglanti.execute("SELECT version_num FROM alembic_version").fetchall()]


def test_veritabani_en_son_revizyonda(test_adresi):
    en_son = ScriptDirectory.from_config(alembic_ayari(test_adresi)).get_current_head()
    assert veritabanindaki_surum(test_adresi) == [en_son]


def test_hepsi_geri_alinip_yeniden_kurulur(test_adresi):
    ayar = alembic_ayari(test_adresi)
    once = tablolar(test_adresi)
    command.downgrade(ayar, "base")
    assert tablolar(test_adresi) == ["alembic_version"]
    assert veritabanindaki_surum(test_adresi) == []
    command.upgrade(ayar, "head")
    assert tablolar(test_adresi) == once


def test_her_adim_tek_tek_geri_alinabilir(test_adresi):
    ayar = alembic_ayari(test_adresi)
    command.downgrade(ayar, "base")
    revizyonlar = reversed(list(ScriptDirectory.from_config(ayar).walk_revisions()))
    for revizyon in revizyonlar:
        command.upgrade(ayar, revizyon.revision)
        command.downgrade(ayar, "-1")
        command.upgrade(ayar, revizyon.revision)
