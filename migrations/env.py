from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from yardim_masasi.veritabani import baglanti_adresi

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Adres alembic.ini'de durmaz, DATABASE_URL'den gelir.
# Testler adresi önceden kendileri verir; o zaman bu satır atlanır.
if config.get_main_option("sqlalchemy.url") is None:
    config.set_main_option("sqlalchemy.url", baglanti_adresi())

# Tablolarımızı SQLAlchemy modeliyle tanımlamadık: autogenerate yok, migration'ları elle yazıyoruz.
target_metadata = None


def run_migrations_offline() -> None:
    """--sql ile çağrılınca: veritabanına bağlanmadan SQL'i ekrana yazar."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Veritabanına bağlanır, bekleyen migration'ları tek bir işlemde uygular."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
