from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel
from azure.storage.blob import BlobServiceClient
import os

# APIRouter 생성
router = APIRouter()

# Azure Blob Storage 설정

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
        blob_client = container_client.get_blob_client(blob=file_name)  # Blob 클라이언트 생성
        blob_client.upload_blob(file.file)  # Blob에 파일 업로드

        # 파일 업로드 성공 후 JSON 응답 반환
        return {"filename": file_name, "detail": "파일이 성공적으로 업로드되었습니다."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
