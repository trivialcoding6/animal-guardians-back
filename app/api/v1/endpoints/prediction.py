from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import CognitiveServicesCredentials  # 수정 필요
import requests
import os
from app.core.config import settings
from typing import List

# APIRouter 생성
router = APIRouter()

# Pydantic 모델 정의
class ImagePredictionRequest(BaseModel):
    image_url: str

class PredictionResult(BaseModel):
    tag_name: str
    probability: float

credentials = CognitiveServicesCredentials(settings.PREDICTION_KEY)

# 클라이언트 초기화
prediction_client = CustomVisionPredictionClient(
    endpoint=settings.PREDICTION_ENDPOINT,
    credentials=credentials  # 'credential' 대신 'credentials' 사용
)
# print(dir(CustomVisionPredictionClient))  # client에서 지원하는 메서드 확인

@router.post("/predict", response_model=List[PredictionResult])
async def predict_image(request: ImagePredictionRequest):
    # URL에서 이미지를 다운로드
    try:
        response = requests.get(request.image_url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise HTTPException(status_code=400, detail="Error fetching image: " + str(err))

    # 예측 요청
    try:
        results = prediction_client.classify_image_url(
            project_id=settings.PROJECT_ID,
            model_name=settings.MODEL_NAME,  # 여기에서 모델 이름 지정
            published_name=settings.MODEL_NAME,  # 배포할 모델의 이름 추가
            url=request.image_url
        )

        # 예측 결과 처리, 확률로 정렬하고 상위 3개 선택
        top_predictions = sorted(results.predictions, key=lambda p: p.probability, reverse=True)[:3]
        
        # JSON 응답 생성
        return [PredictionResult(tag_name=pred.tag_name, probability=pred.probability) for pred in top_predictions]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")  # 예외 시 상세 정보 포함