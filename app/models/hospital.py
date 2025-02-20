from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from uuid import UUID
from .base import Base

if TYPE_CHECKING:
    from .disease import Disease

class Hospital(Base):
    __tablename__ = "hospitals"
    
    disease_id: Mapped[UUID] = mapped_column(ForeignKey("diseases.id", ondelete="CASCADE"), nullable=False)
    hospital_name: Mapped[str] = mapped_column(String(200))
    address: Mapped[str | None] = mapped_column(String)
    contact_info: Mapped[str | None] = mapped_column(String(100))
    website: Mapped[str | None] = mapped_column(String)
    
    disease: Mapped["Disease"] = relationship(back_populates="hospitals")