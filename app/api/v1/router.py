from fastapi import APIRouter
from app.api.v1.endpoints import users  # 엔드포인트 import
from app.api.v1.endpoints import upload  # upload 모듈에서 router를 가져옵니다.

router = APIRouter()

# 다른 라우터들을 포함시킵니다
router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

router.include_router(
    upload.router, # 예측 라우터 추가
    prefix="/upload",  # 해당 라우터의 접두사 정의
    tags=["upload"]
)