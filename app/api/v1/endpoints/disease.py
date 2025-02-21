from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from app.db.session import get_db
from app.schemas.disease import DiseaseSchema, DiseaseCreate, HospitalSchema, InsuranceSchema
from app.crud import disease as disease_crud
from app.crud import hospital as hospital_crud
from app.crud import insurance as insurance_crud
from loguru import logger

router = APIRouter()

@router.get("/", response_model=List[DiseaseSchema])
async def read_diseases(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"Fetching diseases with skip={skip}, limit={limit}")
    diseases = await disease_crud.get_diseases(db, skip=skip, limit=limit)
    return [DiseaseSchema.model_validate(disease) for disease in diseases]

@router.get("/{disease_id}", response_model=DiseaseSchema)
async def read_disease(
    disease_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    disease = await disease_crud.get_disease(db, disease_id)
    if not disease:
        raise HTTPException(status_code=404, detail="Disease not found")
    return DiseaseSchema.model_validate(disease)

@router.get("/type/{disease_type}", response_model=DiseaseSchema)
async def read_disease_by_type(
    disease_type: str,
    db: AsyncSession = Depends(get_db)
):
    disease = await disease_crud.get_disease_by_type(db, disease_type)
    if disease is None:
        raise HTTPException(status_code=404, detail="Disease not found")
    return DiseaseSchema.model_validate(disease)

@router.post("/", response_model=DiseaseSchema)
async def create_disease(
    disease: DiseaseCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await disease_crud.create_disease(db=db, disease=disease)
    except Exception as e:
        logger.error(f"Disease creation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="질병 정보 생성 중 오류가 발생했습니다"
        )

@router.put("/{disease_id}", response_model=DiseaseSchema)
async def update_disease(
    disease_id: UUID,
    disease: DiseaseCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        updated_disease = await disease_crud.update_disease(db, disease_id, disease)
        if updated_disease is None:
            raise HTTPException(status_code=404, detail="Disease not found")
        return DiseaseSchema.model_validate(updated_disease)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Disease update failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="질병 정보 수정 중 오류가 발생했습니다"
        )

@router.delete("/{disease_id}")
async def delete_disease(
    disease_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    try:
        deleted_disease = await disease_crud.delete_disease(db, disease_id)
        if deleted_disease is None:
            raise HTTPException(status_code=404, detail="Disease not found")
        return {"message": "Disease deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Disease deletion failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="질병 정보 삭제 중 오류가 발생했습니다"
        )

@router.get("/{disease_id}/hospitals", response_model=List[HospitalSchema])
async def read_hospitals_by_disease(
    disease_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    hospitals = await hospital_crud.get_hospitals_by_disease(db, disease_id)
    return [HospitalSchema.model_validate(hospital) for hospital in hospitals]

@router.get("/{disease_id}/insurances", response_model=List[InsuranceSchema])
async def read_insurances_by_disease(
    disease_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    insurances = await insurance_crud.get_insurances_by_disease(db, disease_id)
    return [InsuranceSchema.model_validate(insurance) for insurance in insurances]