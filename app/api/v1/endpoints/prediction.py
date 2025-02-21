from fastapi import APIRouter, HTTPException
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials
from app.schemas.predict import PredictionResult, ImagePredictionRequest
import requests
from app.core.config import settings
from typing import List

# APIRouter 생성
router = APIRouter()

credentials = ApiKeyCredentials(in_headers={"Prediction-key": settings.PREDICTION_KEY})

# 클라이언트 초기화
prediction_client = CustomVisionPredictionClient(
    endpoint=settings.PREDICTION_ENDPOINT,
    credentials=credentials
)

@router.post("/predict", response_model=List[PredictionResult])
async def predict_image(request: ImagePredictionRequest):
    # URL에서 이미지를 다운로드
    try:
        response = requests.get(request.image_url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise HTTPException(status_code=400, detail="Error fetching image: " + str(err)) from err

    # 예측 요청
    try:
        image_data = response.content  # 바이트 스트림으로 이미지 데이터 가져오기

        results = prediction_client.classify_image(
            project_id=settings.PROJECT_ID,
            published_name=settings.MODEL_NAME,
            image_data=image_data
        )

        # 예측 결과 처리, 확률로 정렬하고 상위 3개 선택
        top_predictions = sorted(results.predictions, key=lambda p: p.probability, reverse=True)[:3]
        
        return [PredictionResult(tag_name=pred.tag_name, probability=pred.probability) for pred in top_predictions]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}") from e
