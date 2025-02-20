from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from app.models.disease import Disease, DiseaseDetail
from app.models.hospital import Hospital
from app.models.insurance import Insurance
from app.schemas.disease import DiseaseCreate, DiseaseDetailCreate, DiseaseUpdate
from sqlalchemy.orm import selectinload

async def get_diseases(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100
) -> List[Disease]:
    stmt = (
        select(Disease)
        .options(
            selectinload(Disease.details),
            selectinload(Disease.hospitals),
            selectinload(Disease.insurances)
        )
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_disease(db: AsyncSession, disease_id: UUID) -> Optional[Disease]:
    stmt = (
        select(Disease)
        .options(
            selectinload(Disease.details),
            selectinload(Disease.hospitals),
            selectinload(Disease.insurances)
        )
        .where(Disease.id == disease_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_disease_by_name(db: AsyncSession, name: str) -> Optional[Disease]:
    stmt = select(Disease).where(Disease.name == name)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_disease_details(db: AsyncSession, disease_id: UUID) -> List[DiseaseDetail]:
    stmt = select(DiseaseDetail).where(DiseaseDetail.disease_id == disease_id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_disease_details_by_name(
    db: AsyncSession, 
    disease_name: str,
    detail_type: Optional[str] = None
) -> List[DiseaseDetail]:
    stmt = (
        select(DiseaseDetail)
        .join(Disease)
        .where(Disease.name == disease_name)
    )
    if detail_type:
        stmt = stmt.where(DiseaseDetail.detail_type == detail_type)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_disease(db: AsyncSession, disease: DiseaseCreate) -> Disease:
    # 질병 기본 정보 생성
    db_disease = Disease(name=disease.name)
    db.add(db_disease)
    await db.commit()
    await db.refresh(db_disease)
    
    # 상세 정보 추가 - id 자동 생성
    for detail in disease.details:
        db_detail = DiseaseDetail(
            disease_id=db_disease.id,  # 부모 disease의 id 참조
            detail_type=detail.detail_type,
            detail_value=detail.detail_value
        )
        db.add(db_detail)
    
    # 병원 정보 추가 - id 자동 생성
    if disease.hospitals:
        for hospital in disease.hospitals:
            db_hospital = Hospital(
                disease_id=db_disease.id,  # 부모 disease의 id 참조
                hospital_name=hospital.hospital_name,
                address=hospital.address,
                contact_info=hospital.contact_info,
                website=hospital.website
            )
            db.add(db_hospital)
    
    # 보험 정보 추가 - id 자동 생성
    if disease.insurances:
        for insurance in disease.insurances:
            db_insurance = Insurance(
                disease_id=db_disease.id,  # 부모 disease의 id 참조
                insurance_name=insurance.insurance_name,
                policy_details=insurance.policy_details,
                website=insurance.website
            )
            db.add(db_insurance)
    
    await db.commit()
    await db.refresh(db_disease)
    return db_disease

async def update_disease(
    db: AsyncSession, 
    disease_id: UUID, 
    disease: DiseaseUpdate
) -> Optional[Disease]:
    db_disease = await get_disease(db, disease_id)
    if not db_disease:
        return None
    
    # 기본 정보 업데이트
    db_disease.name = disease.name
    if disease.category:
        db_disease.category = disease.category
    
    # 상세 정보 업데이트 (기존 정보 삭제 후 새로 추가)
    query = select(DiseaseDetail).where(DiseaseDetail.disease_id == disease_id)
    result = await db.execute(query)
    existing_details = result.scalars().all()
    for detail in existing_details:
        await db.delete(detail)
    
    for detail in disease.details:
        db_detail = DiseaseDetail(
            disease_id=disease_id,
            detail_type=detail.detail_type,
            detail_value=detail.detail_value
        )
        db.add(db_detail)
    
    await db.commit()
    await db.refresh(db_disease)
    return db_disease

async def delete_disease(
    db: AsyncSession, 
    disease_id: UUID
) -> bool:
    disease = await get_disease(db, disease_id)
    if not disease:
        return False
    
    await db.delete(disease)
    await db.commit()
    return True

# 상세 정보 관련 추가 함수들
async def add_disease_detail(
    db: AsyncSession, 
    disease_id: UUID, 
    detail: DiseaseDetailCreate
) -> DiseaseDetail:
    db_detail = DiseaseDetail(
        disease_id=disease_id,
        detail_type=detail.detail_type,
        detail_value=detail.detail_value
    )
    db.add(db_detail)
    await db.commit()
    await db.refresh(db_detail)
    return db_detail

async def delete_disease_detail(
    db: AsyncSession, 
    detail_id: UUID
) -> Optional[DiseaseDetail]:
    query = select(DiseaseDetail).where(DiseaseDetail.id == detail_id)
    result = await db.execute(query)
    detail = result.scalar_one_or_none()
    if detail:
        await db.delete(detail)
        await db.commit()
    return detail