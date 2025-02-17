from fastapi import APIRouter
from app.api.v1.endpoints import users  # 엔드포인트 import

router = APIRouter()

# 다른 라우터들을 포함시킵니다
router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)