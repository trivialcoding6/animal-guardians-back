import torch
import requests
from io import BytesIO
from typing import List
from PIL import Image
from fastapi import HTTPException, status
import logging
import torch.nn as nn
from torchvision import models
import json

from azure.storage.blob import BlobServiceClient
import torchvision.transforms as transforms

from app.schemas.predict import PredictionResult
from app.core.config import settings

from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials

from app.ai_models.architectures import EnsembleModel

logger = logging.getLogger(__name__)

async def predict_pet_disease_torch(image_url: str, pet_type: str) -> List[PredictionResult]:
    """
    1) pet_type에 따라 Azure Blob Storage에서 모델 파일 다운로드
    2) 모델 로드(PyTorch)
    3) image_url에서 이미지를 가져와 전처리
    4) 추론 & 확률 계산
    5) 상위 3개의 결과(PredictionResult)를 반환
    """

    # -----------------------------
    # (A) pet_type에 따라 모델 & 라벨 선택
    # -----------------------------
    if pet_type == "dog":
        model_file_name = settings.TORCH_DOG_MODEL_NAME
        disease_labels = settings.DOG_LABELS
    elif pet_type == "cat":
        model_file_name = settings.TORCH_CAT_MODEL_NAME
        disease_labels = settings.CAT_LABELS
    else:
        raise ValueError(f"지원되지 않는 pet_type: {pet_type}")

    # -----------------------------
    # (B) Blob Storage에서 모델 및 라벨 다운로드
    # -----------------------------
    blob_service_client = BlobServiceClient.from_connection_string(settings.BLOB_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(settings.BLOB_CONTAINER_NAME)
    
    # 모델 파일 다운로드
    model_blob_client = container_client.get_blob_client(model_file_name)
    model_bytes = model_blob_client.download_blob().readall()

    # 라벨 파일 다운로드 (모델 파일명 + .json)
    label_file_name = f"{disease_labels}.json"
    label_blob_client = container_client.get_blob_client(label_file_name)

    try:
        label_bytes = label_blob_client.download_blob().readall()
        disease_labels = json.loads(label_bytes.decode('utf-8'))
        logger.info(f"Loaded labels from Blob Storage: {disease_labels}")
    except Exception as e:
        logger.error(f"라벨 파일 로드 실패: {label_file_name}, {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"라벨 정보 로드 실패: {str(e)}"
        )

    # -----------------------------
    # (C) PyTorch 모델 로드
    # -----------------------------
    # 아키텍처 분리 후 간소화된 모델 생성
    try:
        checkpoint = torch.load(BytesIO(model_bytes), map_location=torch.device('cpu'))
        
        if 'resnet' in checkpoint and 'efficientnet' in checkpoint:
            is_ensemble = True
            # 개별 모델 초기화 (num_classes 파라미터 사용)
            resnet = models.resnet18(weights=None)
            resnet.fc = nn.Sequential(
                nn.Dropout(0.7),
                nn.Linear(resnet.fc.in_features, len(disease_labels))
            )
            resnet.load_state_dict(checkpoint['resnet'])

            efficientnet = models.efficientnet_b0(weights=None)
            efficientnet.classifier[1] = nn.Sequential(
                nn.Dropout(0.7),
                nn.Linear(efficientnet.classifier[1].in_features, 256),
                nn.ReLU(),
                nn.Linear(256, len(disease_labels))
            )
            efficientnet.load_state_dict(checkpoint['efficientnet'])

            # 앙상블 모델 초기화 방식 수정 (num_classes 파라미터 제거)
            model = EnsembleModel(models=[resnet, efficientnet])
        else:
            is_ensemble = False
            # 단일 모델 초기화 (num_classes 파라미터 사용)
            if "resnet" in model_file_name.lower():
                model = models.resnet18(weights=None)
                model.fc = nn.Sequential(
                    nn.Dropout(0.7),
                    nn.Linear(model.fc.in_features, len(disease_labels))
                )
                model.load_state_dict(checkpoint)
            elif "efficientnet" in model_file_name.lower():
                model = models.efficientnet_b0(weights=None)
                model.classifier[1] = nn.Sequential(
                    nn.Dropout(0.7),
                    nn.Linear(model.classifier[1].in_features, 256),
                    nn.ReLU(),
                    nn.Linear(256, len(disease_labels))
                )
                model.load_state_dict(checkpoint)
            model.load_state_dict(checkpoint)
    except RuntimeError as e:
        logger.error(f"모델 로드 실패 (pet_type: {pet_type}, model: {model_file_name}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"모델 로드 중 오류 발생: {str(e)}"
        ) from e
        
    model.eval()

    # -----------------------------
    # (D) image_url에서 이미지를 가져와 전처리
    # -----------------------------
    response = requests.get(image_url)
    image_data = response.content

    # PIL Image 로딩
    image = Image.open(BytesIO(image_data)).convert("RGB")

    # 전처리 파이프라인 (예시)
    transform = transforms.Compose([
        transforms.Resize((224, 224)),  # 모델 입력 크기에 맞춤
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        ),
    ])
    input_tensor = transform(image).unsqueeze(0)  # (1, C, H, W)

    # -----------------------------
    # (E) 모델 추론
    # -----------------------------
    with torch.no_grad():
        outputs = model(input_tensor)
        # 앙상블인 경우 이미 평균 처리됨
        probs_tensor = torch.softmax(outputs, dim=1) 
        probs = probs_tensor[0]

    # -----------------------------
    # (F) 상위 3개 결과 선별
    # -----------------------------
    # 만약 클래스 수가 3개 미만인 경우도 대비하려면 min() 처리
    topk = min(3, len(disease_labels))

    top_probs, top_idxs = torch.topk(probs, topk)
    top_probs = top_probs.tolist()
    top_idxs = top_idxs.tolist()

    # PredictionResult 리스트 생성
    prediction_results = []
    for i in range(topk):
        idx = top_idxs[i]
        label_name = disease_labels[idx]
        probability = top_probs[i]
        prediction_results.append(
            PredictionResult(tag_name=label_name, probability=probability)
        )

    return prediction_results

async def predict_pet_disease_custom_vision(image_url: str, pet_type: str) -> List[PredictionResult]:
    if pet_type == "dog":
        model_name = settings.DOG_MODEL_NAME
        project_id = settings.DOG_PROJECT_ID
    elif pet_type == "cat":
        model_name = settings.CAT_MODEL_NAME
        project_id = settings.CAT_PROJECT_ID
    else:
        # 그 외의 경우 예외 처리하거나, 기본값 지정
        raise ValueError(f"지원되지 않는 pet_type: {pet_type}")
    
    credentials = ApiKeyCredentials(in_headers={"Prediction-key": settings.PREDICTION_KEY})

# 클라이언트 초기화
    prediction_client = CustomVisionPredictionClient(
        endpoint=settings.PREDICTION_ENDPOINT,
        credentials=credentials
    )

    try:
        response = requests.get(image_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"이미지 다운로드 실패 (URL: {image_url}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"이미지 다운로드 실패: {str(e)}"
        ) from e

    # 예측 요청
    try:
        image_data = response.content  # 바이트 스트림으로 이미지 데이터 가져오기

        results = prediction_client.classify_image(
            project_id=project_id,
            published_name=model_name,
            image_data=image_data
        )

        # 예측 결과 처리, 확률로 정렬하고 상위 3개 선택
        top_predictions = sorted(results.predictions, key=lambda p: p.probability, reverse=True)[:3]
        
        return [PredictionResult(tag_name=pred.tag_name, probability=pred.probability) for pred in top_predictions]
    except Exception as e:
        logger.error(f"Custom Vision 예측 실패 (pet_type: {pet_type}): {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"예측 서비스 오류: {str(e)}"
        ) from e