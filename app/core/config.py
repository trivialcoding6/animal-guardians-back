# core/config.py
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Disease API"
    DB_ECHO_LOG: bool = True
    
    # 데이터베이스 설정
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    SECRET_KEY: str
    DATABASE_URL: str

    AZURE_CONNECTION_STRING: str
    STORAGE_NAME: str

    PREDICTION_ENDPOINT: str
    PREDICTION_KEY: str
    
    DOG_PROJECT_ID: str
    DOG_MODEL_NAME: str

    CAT_PROJECT_ID: str
    CAT_MODEL_NAME: str

    BLOB_CONTAINER_NAME: str
    BLOB_CONNECTION_STRING: str

    TORCH_DOG_MODEL_NAME: str
    TORCH_CAT_MODEL_NAME: str
    
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def SYNC_DATABASE_URL(self) -> str:
        """Alembic 마이그레이션용 동기 URL"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    model_config = ConfigDict(
        env_file=".env",
        extra="allow"  # 추가 필드 허용
    )

settings = Settings()