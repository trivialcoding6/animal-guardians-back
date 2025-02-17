import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import engine_from_config
from sqlmodel import SQLModel
from alembic import context

from app.core.config import settings
from app.models import *  # 모든 모델 임포트

# Alembic 설정 파일 로드
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 메타데이터 대상 설정
target_metadata = SQLModel.metadata

def get_url():
    return settings.SQLALCHEMY_DATABASE_URI

def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # 컬럼 타입 변경 감지
        compare_server_default=True,  # 기본값 변경 감지
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()