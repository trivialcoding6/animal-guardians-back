from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# CORS 미들웨어 설정
origins = [
    "http://localhost:3000",     # React 개발 서버
    "https://yourfrontend.com",  # 프로덕션 프론트엔드 도메인
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix="/api/v1")