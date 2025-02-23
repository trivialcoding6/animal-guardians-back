import torch
import requests
from io import BytesIO
from typing import List
from PIL import Image
from fastapi import HTTPException, status
import logging

from azure.storage.blob import BlobServiceClient
import torchvision.transforms as transforms

from app.schemas.predict import PredictionResult
from app.core.config import settings

from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials

from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights

logger = logging.getLogger(__name__)

DOG_MODEL_NAME = "efficientnet_dog_best_20250223003417.pth"
CAT_MODEL_NAME = "efficientnet_cat_best_20250223011242.pth"

# 분류할 질병 라벨 목록 (모델 아웃풋 순서에 대응해야 함, 예시는 5개)
DOG_LABELS = [
    "A1",
    "A2",
    "A3",
    "A4",
    "A5",
    "A6",
    "Negative"
]

CAT_LABELS = [
    "A2",
    "A4",
    "A6"
]

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
        model_file_name = DOG_MODEL_NAME
        disease_labels = DOG_LABELS
    elif pet_type == "cat":
        model_file_name = CAT_MODEL_NAME
        disease_labels = CAT_LABELS
    else:
        # 그 외의 경우 예외 처리하거나, 기본값 지정
        raise ValueError(f"지원되지 않는 pet_type: {pet_type}")

    # -----------------------------
    # (B) Blob Storage에서 모델 다운로드
    # -----------------------------
    blob_service_client = BlobServiceClient.from_connection_string(settings.BLOB_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(settings.BLOB_CONTAINER_NAME)
    blob_client = container_client.get_blob_client(model_file_name)

    # 모델 바이너리 다운로드
    model_bytes = blob_client.download_blob().readall()

    # -----------------------------
    # (C) PyTorch 모델 로드
    # -----------------------------
    # 정확한 모델 아키텍처 재현 필요
    model = efficientnet_b0(weights=EfficientNet_B0_Weights.IMAGENET1K_V1)
    model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, len(disease_labels))  # 최종 레이어 조정
    
    # CPU 환경에서 로드하도록 설정
    try:
        model.load_state_dict(
            torch.load(BytesIO(model_bytes), map_location=torch.device('cpu'))
        )
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
        outputs = model(input_tensor)  # shape: (batch_size, num_classes)
        probs = torch.softmax(outputs, dim=1)[0]  # (num_classes, )

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