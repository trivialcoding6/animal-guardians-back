from fastapi import FastAPI
from app.api.v1.router import router as api_v1_router
from app.db.base import create_db_and_tables
from app.core.logging import setup_logging
from loguru import logger

app = FastAPI(title="My API")

@app.on_event("startup")
def on_startup():
    setup_logging()
    logger.info("Application starting up...")
    create_db_and_tables()

app.include_router(api_v1_router, prefix="/api/v1")