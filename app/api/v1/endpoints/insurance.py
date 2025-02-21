from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from app.db.session import get_db
from app.schemas.insurance import InsuranceSchema, InsuranceCreate, InsuranceUpdate
from app.crud import insurance as insurance_crud
from app.crud import disease as disease_crud

router = APIRouter()

@router.get("/", response_model=List[InsuranceSchema])
async def read_insurances(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    insurances = await insurance_crud.get_insurances(db, skip=skip, limit=limit)
    return [InsuranceSchema.model_validate(insurance) for insurance in insurances]

@router.get("/{insurance_id}", response_model=InsuranceSchema)
async def read_insurance(
    insurance_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    insurance = await insurance_crud.get_insurance(db, insurance_id)
    if insurance is None:
        raise HTTPException(status_code=404, detail="Insurance not found")
    return insurance

@router.get("/disease/{disease_id}", response_model=List[InsuranceSchema])
async def read_insurances_by_disease(
    disease_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    insurances = await insurance_crud.get_insurances_by_disease(db, disease_id)
    return [InsuranceSchema.model_validate(insurance) for insurance in insurances]

@router.post("/disease/{disease_id}", response_model=InsuranceSchema)
async def create_insurance(
    disease_id: UUID,
    insurance: InsuranceCreate,
    db: AsyncSession = Depends(get_db)
):
    disease = await disease_crud.get_disease(db, disease_id)
    if not disease:
        raise HTTPException(status_code=404, detail="Disease not found")
    return await insurance_crud.create_insurance(db=db, insurance=insurance, disease_id=disease_id)

@router.put("/{insurance_id}", response_model=InsuranceSchema)
async def update_insurance(
    insurance_id: UUID,
    insurance: InsuranceUpdate,
    db: AsyncSession = Depends(get_db)
):
    updated_insurance = await insurance_crud.update_insurance(db, insurance_id, insurance)
    if updated_insurance is None:
        raise HTTPException(status_code=404, detail="Insurance not found")
    return updated_insurance

@router.delete("/{insurance_id}")
async def delete_insurance(
    insurance_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    deleted_insurance = await insurance_crud.delete_insurance(db, insurance_id)
    if deleted_insurance is None:
        raise HTTPException(status_code=404, detail="Insurance not found")
    return {"message": "Insurance deleted successfully"}