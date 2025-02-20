from pydantic import BaseModel

class Upload(BaseModel):
    filename: str  # 이전에는 UUID 기반 파일명
    filename: str  # 원본 파일명
    url: str
    class Config:
        schema_extra = {
            "example": {
                "filename": "example.jpg",
                "url": "https://storage.blob.core.windows.net/container/uuid.jpg"
            }
        }