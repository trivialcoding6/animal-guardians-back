import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import user as user_crud
from app.schemas.user import UserCreate

@pytest.mark.asyncio
async def test_create_user(session: AsyncSession):
    user_data = UserCreate(
        id=1,
        name="Test User",
        email="test@example.com",
        password="testpassword"
    )
    user = await user_crud.create_user(session, user_data)
    assert user.email == "test@example.com"
    assert user.name == "Test User"

@pytest.mark.asyncio
async def test_get_user_by_email(session: AsyncSession):
    # 사용자 생성
    user_data = UserCreate(
        id=1,
        name="Test User",
        email="test@example.com",
        password="testpassword"
    )
    await user_crud.create_user(session, user_data)
    
    # 이메일로 사용자 조회
    user = await user_crud.get_user_by_email(session, "test@example.com")
    assert user is not None
    assert user.email == "test@example.com"