from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from app.db.session import get_db
from app.schemas.hospital import HospitalSchema, HospitalCreate, HospitalUpdate
from app.crud import hospital as hospital_crud
from loguru import logger

router = APIRouter()

@router.get("/", response_model=List[HospitalSchema])
async def read_hospitals(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    hospitals = await hospital_crud.get_hospitals(db, skip=skip, limit=limit)
    return [HospitalSchema.model_validate(hospital) for hospital in hospitals]

@router.get("/{hospital_id}", response_model=HospitalSchema)
async def read_hospital(
    hospital_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    hospital = await hospital_crud.get_hospital(db, hospital_id)
    if hospital is None:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return hospital

@router.get("/disease/{disease_id}", response_model=List[HospitalSchema])
async def read_hospitals_by_disease(
    disease_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    hospitals = await hospital_crud.get_hospitals_by_disease(db, disease_id)
    return hospitals

@router.post("/disease/{disease_id}", response_model=HospitalSchema)
async def create_hospital(
    disease_id: UUID,
    hospital: HospitalCreate,
    db: AsyncSession = Depends(get_db)
):
    return await hospital_crud.create_hospital(db=db, hospital=hospital, disease_id=disease_id)

@router.put("/{hospital_id}", response_model=HospitalSchema)
async def update_hospital(
    hospital_id: UUID,
    hospital: HospitalUpdate,
    db: AsyncSession = Depends(get_db)
):
    updated_hospital = await hospital_crud.update_hospital(db, hospital_id, hospital)
    if updated_hospital is None:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return updated_hospital

@router.delete("/{hospital_id}")
async def delete_hospital(
    hospital_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    deleted_hospital = await hospital_crud.delete_hospital(db, hospital_id)
    if deleted_hospital is None:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return {"message": "Hospital deleted successfully"}