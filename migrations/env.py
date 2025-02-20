import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import engine_from_config
from alembic import context

from app.core.config import settings
from app.models.base import Base  # SQLAlchemy Base 클래스 임포트

# Alembic 설정 파일 로드
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 동기 엔진 사용
target_metadata = Base.metadata

def get_url():
    return settings.SYNC_DATABASE_URL  # 동기 URL 사용

def run_migrations_offline():
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=get_url(),  # 동기 URL 사용
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
