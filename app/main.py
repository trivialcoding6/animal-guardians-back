from fastapi import FastAPI
from app.api.v1.router import router as api_v1_router
from app.db.base import create_db_and_tables

app = FastAPI(title="My API")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(api_v1_router, prefix="/api/v1")