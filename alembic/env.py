import os
import sys
from logging.config import fileConfig
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

from backend.models import Base

target_metadata = Base.metadata
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def get_url():
    migration_url = os.getenv("MIGRATION_DATABASE_URL")

    if migration_url:
        print(migration_url)
        return migration_url

    raise ValueError("Url not find")


def run_migrations_offline():
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        version_table_schema="schedule_schema"
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    url = get_url()
    url_with_schema = f"{url}?options=-csearch_path%3Dschedule_schema"

    connectable = engine_from_config(
        {"sqlalchemy.url": url_with_schema},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            version_table_schema=None,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()