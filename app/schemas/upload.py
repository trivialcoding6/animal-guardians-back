from pydantic import BaseModel

class Upload(BaseModel):
    filename: str
    url: str
    class Config:
        schema_extra = {
            "example": {
                "filename": "example.jpg",
                "url": "https://storage.blob.core.windows.net/container/uuid.jpg"
            }
        }