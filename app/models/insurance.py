from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text
from uuid import UUID
from .base import Base

class Insurance(Base):
    __tablename__ = "insurances"
    
    disease_id: Mapped[UUID] = mapped_column(ForeignKey("diseases.id", ondelete="CASCADE"), nullable=False)
    insurance_name: Mapped[str] = mapped_column(String(200))
    policy_details: Mapped[str] = mapped_column(Text)
    website: Mapped[str | None] = mapped_column(String)
    
    disease: Mapped["Disease"] = relationship(back_populates="insurances")