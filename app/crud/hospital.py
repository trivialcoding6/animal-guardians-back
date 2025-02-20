from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from app.models.hospital import Hospital
from app.schemas.hospital import HospitalCreate, HospitalUpdate

async def get_hospitals(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100
) -> List[Hospital]:
    stmt = select(Hospital).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_hospital(db: AsyncSession, hospital_id: UUID) -> Optional[Hospital]:
    stmt = select(Hospital).where(Hospital.id == hospital_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_hospitals_by_disease(db: AsyncSession, disease_id: UUID) -> List[Hospital]:
    stmt = select(Hospital).where(Hospital.disease_id == disease_id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_hospital(db: AsyncSession, hospital: HospitalCreate, disease_id: UUID) -> Hospital:
    db_hospital = Hospital(
        disease_id=disease_id,
        hospital_name=hospital.hospital_name,
        address=hospital.address,
        contact_info=hospital.contact_info,
        website=hospital.website
    )
    db.add(db_hospital)
    await db.commit()
    await db.refresh(db_hospital)
    return db_hospital

async def update_hospital(db: AsyncSession, hospital_id: UUID, hospital: HospitalUpdate) -> Optional[Hospital]:
    db_hospital = await get_hospital(db, hospital_id)
    if not db_hospital:
        return None
    
    hospital_data = hospital.model_dump(exclude_unset=True)
    for key, value in hospital_data.items():
        setattr(db_hospital, key, value)
    
    await db.commit()
    await db.refresh(db_hospital)
    return db_hospital

async def delete_hospital(
    db: AsyncSession, 
    hospital_id: UUID
) -> Optional[Hospital]:
    hospital = await get_hospital(db, hospital_id)
    if hospital:
        await db.delete(hospital)
        await db.commit()
    return hospital

async def delete_hospitals_by_disease(
    db: AsyncSession, 
    disease_id: UUID
) -> None:
    stmt = select(Hospital.__table__.columns).where(Hospital.disease_id == disease_id)
    result = await db.execute(stmt)
    hospitals = result.scalars().all()
    for hospital in hospitals:
        await db.delete(hospital)
    await db.commit()