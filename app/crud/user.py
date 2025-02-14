# crud/user.py
from sqlalchemy.orm import Session
from ..models.user import User
from ..schemas.user import UserCreate
from sqlalchemy import select


async def get_users(db: Session, skip: int = 0, limit: int = 100):
    query = select(User).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_user_by_email(db: Session, email: str):
    query = select(User).filter(User.email == email)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def create_user(db: Session, user: UserCreate):
    db_user = User(
        id=user.id,
        email=user.email,
        name=user.name
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user