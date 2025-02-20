from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1.router import router as api_v1_router
from app.db.base import init_db
from app.core.logging import setup_logging
from loguru import logger
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 실행
    setup_logging()
    logger.info("Application starting up...")
    try:
        await init_db()
        yield
    except asyncio.CancelledError:
        logger.warning("Lifespan tasks cancelled")
    finally:
        # 종료 시 실행
        logger.info("Application shutting down...")

app = FastAPI(title="My API", lifespan=lifespan)
app.include_router(api_v1_router, prefix="/api/v1")