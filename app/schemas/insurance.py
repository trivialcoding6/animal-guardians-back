from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID

class InsuranceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    disease_id: UUID
    insurance_name: str
    policy_details: Optional[str] = None
    website: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class InsuranceCreate(BaseModel):
    insurance_name: str
    policy_details: Optional[str] = None
    website: Optional[str] = None

class InsuranceUpdate(BaseModel):
    insurance_name: Optional[str] = None
    policy_details: Optional[str] = None
    website: Optional[str] = None