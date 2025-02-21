from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional
from .hospital import HospitalSchema, HospitalCreate
from .insurance import InsuranceSchema, InsuranceCreate
from uuid import UUID

class DiseaseDetailSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    detail_type: str
    detail_value: str
    created_at: datetime

class DiseaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    type: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    details: List[DiseaseDetailSchema]
    hospitals: List[HospitalSchema] = []
    insurances: List[InsuranceSchema] = []

class DiseaseDetailCreate(BaseModel):
    detail_type: str
    detail_value: str


class DiseaseCreate(BaseModel):
    name: str
    type: Optional[str] = None
    details: List[DiseaseDetailCreate] = []
    hospitals: List[HospitalCreate] = []
    insurances: List[InsuranceCreate] = []

class DiseaseUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    details: Optional[List[DiseaseDetailCreate]] = None
    hospitals: Optional[List[HospitalCreate]] = None
    insurances: Optional[List[InsuranceCreate]] = None
