import pytest
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import MetaData
from app.main import app
from app.db.session import get_db

# SQLite in-memory 데이터베이스 사용
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Base 클래스 생성
Base = declarative_base()

# 테스트용 엔진 생성
engine_test = create_async_engine(
    TEST_DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False}
)

# 테스트용 세션 생성
async_session_test = sessionmaker(
    engine_test,
    class_=AsyncSession,
    expire_on_commit=False
)

# @pytest.fixture(scope="session")
# def event_loop():
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()

# 테스트용 DB 세션
async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_test() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

@pytest.fixture(autouse=True)
async def setup_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_test() as session:
        yield session

@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    # 의존성 오버라이드
    app.dependency_overrides[get_db] = override_get_db
    
    # TestClient 초기화 수정
    with TestClient(app, base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()