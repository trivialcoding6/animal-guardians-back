from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID

class HospitalSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    disease_id: UUID
    hospital_name: str
    address: str
    contact_info: str
    website: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class HospitalCreate(BaseModel):
    hospital_name: str
    address: Optional[str] = None
    contact_info: Optional[str] = None
    website: Optional[str] = None

class HospitalUpdate(BaseModel):
    hospital_name: Optional[str] = None
    address: Optional[str] = None
    contact_info: Optional[str] = None
    website: Optional[str] = None