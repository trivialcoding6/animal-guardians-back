from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import Settings

settings = Settings()

# 동기 엔진
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,
)

# 비동기 엔진
async_engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=True,
)

async_session = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

# 데이터베이스 테이블 생성
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)