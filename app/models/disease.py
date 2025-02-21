from __future__ import annotations
from typing import List, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey
from uuid import UUID
from .base import Base

if TYPE_CHECKING:
    from .hospital import Hospital
    from .insurance import Insurance
    

class Disease(Base):
    __tablename__ = "diseases"
    
    name: Mapped[str] = mapped_column(String(100), index=True)

    type: Mapped[str] = mapped_column(String(100), index=True, nullable=True)
    
    details: Mapped[List["DiseaseDetail"]] = relationship(
        back_populates="disease",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    hospitals: Mapped[List["Hospital"]] = relationship(
        back_populates="disease",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    insurances: Mapped[List["Insurance"]] = relationship(
        back_populates="disease",
        cascade="all, delete-orphan",
        lazy="selectin"
    )


# 2. 질병 상세 정보 (disease_details) 테이블 모델
class DiseaseDetail(Base):
    __tablename__ = "disease_details"
    
    disease_id: Mapped[UUID] = mapped_column(ForeignKey("diseases.id", ondelete="CASCADE"), nullable=False)
    detail_type: Mapped[str] = mapped_column(String(50))  # 예: "증상", "원인", "케어방법"
    detail_value: Mapped[str] = mapped_column(Text)
    
    disease: Mapped["Disease"] = relationship(back_populates="details")

