from fastapi import APIRouter
from app.api.v1.endpoints import upload  # upload 모듈에서 router를 가져옵니다.
from app.api.v1.endpoints import prediction
from app.api.v1.endpoints import disease
from app.api.v1.endpoints import hospital
from app.api.v1.endpoints import insurance

router = APIRouter()

router.include_router(
    upload.router, # 예측 라우터 추가
    prefix="/upload",  # 해당 라우터의 접두사 정의
    tags=["upload"]
)

router.include_router(
    prediction.router, 
    prefix="/api/v1", 
    tags=["prediction"]
    )

router.include_router(
    disease.router,
    prefix="/diseases",
    tags=["diseases"]
)

router.include_router(
    hospital.router,
    prefix="/hospitals",
    tags=["hospitals"]
)

router.include_router(
    insurance.router,
    prefix="/insurances",
    tags=["insurances"]
)
