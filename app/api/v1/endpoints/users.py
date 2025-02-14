# api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from ....schemas import user as user_schema
from ....crud import user as user_crud
from ....db.session import get_db
from typing import List

router = APIRouter()

@router.get("/", response_model=List[user_schema.UserCreate])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    users = await user_crud.get_users(db, skip=skip, limit=limit)
    return users

@router.post("/", response_model=user_schema.UserCreate)
async def create_user(
    user: user_schema.UserCreate,
    db: Session = Depends(get_db)
):
    db_user = await user_crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="이미 등록된 이메일입니다."
        )
    return await user_crud.create_user(db=db, user=user)