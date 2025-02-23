from fastapi import APIRouter, HTTPException
from app.schemas.predict import PredictionResult, ImagePredictionRequest
from app.services.predict_service import predict_pet_disease_torch, predict_pet_disease_custom_vision
import requests
from typing import List

# APIRouter 생성
router = APIRouter()

@router.post("/vision/predict", response_model=List[PredictionResult])
async def predict_image(request: ImagePredictionRequest):
    try:
        predictions = await predict_pet_disease_custom_vision(request.image_url, request.pet_type)
        return predictions
    except ValueError as e:  # pet_type 오류 처리
        raise HTTPException(status_code=400, detail=str(e))
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Image download failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.post("/torch/predict", response_model=List[PredictionResult])
async def predict_image(request: ImagePredictionRequest):
    """
    이미지를 받아서 반려동물의 타입(강아지/고양이)에 따라 
    Azure Blob Storage에서 해당 모델을 가져오고 
    예측 결과를 반환한다.
    """
    try:
        predictions = await predict_pet_disease_torch(request.image_url, request.pet_type)
        return predictions
    except ValueError as e:  # pet_type 유효성 검사
        raise HTTPException(status_code=400, detail=str(e))
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Image download failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")