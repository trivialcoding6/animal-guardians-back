from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from app.models.insurance import Insurance
from app.schemas.insurance import InsuranceCreate, InsuranceUpdate

async def get_insurances(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100
) -> List[Insurance]:
    stmt = select(Insurance).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_insurance(db: AsyncSession, insurance_id: UUID) -> Optional[Insurance]:
    stmt = select(Insurance).where(Insurance.id == insurance_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_insurances_by_disease(
    db: AsyncSession, 
    disease_id: UUID
) -> List[Insurance]:
    stmt = select(Insurance).where(Insurance.disease_id == disease_id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_insurance(
    db: AsyncSession, 
    insurance: InsuranceCreate, 
    disease_id: UUID
) -> Insurance:
    db_insurance = Insurance(
        disease_id=disease_id,
        insurance_name=insurance.insurance_name,
        policy_details=insurance.policy_details,
        website=insurance.website
    )
    db.add(db_insurance)
    await db.commit()
    await db.refresh(db_insurance)
    return db_insurance

async def update_insurance(
    db: AsyncSession, 
    insurance_id: UUID, 
    insurance: InsuranceUpdate
) -> Optional[Insurance]:
    db_insurance = await get_insurance(db, insurance_id)
    if not db_insurance:
        return None
    
    insurance_data = insurance.model_dump(exclude_unset=True)
    for key, value in insurance_data.items():
        setattr(db_insurance, key, value)
    
    await db.commit()
    await db.refresh(db_insurance)
    return db_insurance

async def delete_insurance(
    db: AsyncSession, 
    insurance_id: UUID
) -> Optional[Insurance]:
    insurance = await get_insurance(db, insurance_id)
    if insurance:
        await db.delete(insurance)
        await db.commit()
    return insurance

# 특정 질병에 대한 모든 보험 삭제
async def delete_insurances_by_disease(
    db: AsyncSession, 
    disease_id: UUID
) -> None:
    stmt = select(Insurance.__table__.columns).where(Insurance.disease_id == disease_id)
    result = await db.execute(stmt)
    insurances = result.scalars().all()
    for insurance in insurances:
        await db.delete(insurance)
    await db.commit()