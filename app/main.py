from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1.router import router as api_v1_router
from app.db.base import create_db_and_tables
from app.core.logging import setup_logging
from loguru import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 실행
    setup_logging()
    logger.info("Application starting up...")
    create_db_and_tables()
    yield
    # 종료 시 실행
    logger.info("Application shutting down...")

app = FastAPI(title="My API", lifespan=lifespan)
app.include_router(api_v1_router, prefix="/api/v1")