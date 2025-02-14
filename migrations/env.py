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
fileConfig(config.config_file_name)

# SQLModel의 메타데이터를 Alembic의 대상으로 지정
target_metadata = SQLModel.metadata

# 데이터베이스 URL 가져오는 함수
def get_url():
    return settings.SQLALCHEMY_DATABASE_URI

# 오프라인 모드에서 마이그레이션 실행
def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# 온라인 모드에서 마이그레이션 실행 (비동기)
async def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    url = get_url()
    configuration["sqlalchemy.url"] = url

    # 데이터베이스 엔진 설정
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # 비동기 연결로 마이그레이션 실행
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

# 메인 실행 부분
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())