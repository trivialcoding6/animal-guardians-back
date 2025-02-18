from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel
from azure.storage.blob import BlobServiceClient
from app.core.config import settings
from app.schemas.upload import Upload
import os

# APIRouter 생성
router = APIRouter()

@router.post("/", response_model=Upload)
async def upload(file: UploadFile):
    # Azure Blob 서비스 클라이언트 생성
    blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_CONNECTION_STRING)

    # Blob 컨테이너 클라이언트 생성
    container_client = blob_service_client.get_container_client(settings.CONTAINER_NAME)

    try:
    # 파일 크기 검증 (예: 10MB 제한)
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        file_size = 0
        contents = await file.read()
        file_size = len(contents)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File size exceeds maximum limit")
        
        # 파일 형식 검증
        ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="File type not allowed")
        
        # 안전한 파일 이름 생성
        import uuid
        file_name = f"{uuid.uuid4()}{file_ext}"

        # Azure Blob Storage에 파일 업로드
        blob_client = container_client.get_blob_client(blob=file_name)
        blob_client.upload_blob(contents)

        # 업로드된 Blob의 URL 생성
        blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{settings.container_name}/{file_name}"

        # 파일 업로드 성공 후 JSON 응답 반환
        return {"filename": file_name, "url": blob_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
