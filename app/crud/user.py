# crud/user.py
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    query = select(User).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_user_by_email(db: AsyncSession, email: str):
    statement = select(User).where(User.email == email)
    result = await db.execute(statement)
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user: UserCreate):
    db_user = User(
        email=user.email,
        name=user.name,
        password=user.password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user