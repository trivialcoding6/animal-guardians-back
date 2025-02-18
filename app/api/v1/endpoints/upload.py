from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel
from azure.storage.blob import BlobServiceClient
import os

# APIRouter 생성
router = APIRouter()

# Azure Blob Storage 설정
# 애저 커넥팅
# 컨테이너 이름

class ImageURL(BaseModel):
    url: str

@router.post("/")
async def upload(file: UploadFile = File(...)):
    # Azure Blob 서비스 클라이언트 생성
    blob_service_client = BlobServiceClient.from_connection_string("애저 커넥팅")

    # Blob 컨테이너 클라이언트 생성
    container_client = blob_service_client.get_container_client("컨테이너 이름")  # get_container_client 사용

    try:
        # 파일 이름 설정
        file_name = file.filename

        # Azure Blob Storage에 파일 업로드
        blob_client = container_client.get_blob_client(blob=file_name)
        blob_client.upload_blob(file.file)

        # 업로드된 Blob의 URL 생성
        blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{CONTAINER_NAME}/{file_name}"

        # 파일 업로드 성공 후 JSON 응답 반환
        return {"filename": file_name, "url": blob_url}


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))