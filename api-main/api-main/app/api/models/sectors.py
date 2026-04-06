from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid_utils import uuid7

from app.db.session import Base

if TYPE_CHECKING:
    from app.api.models.institutions import Institution
    from app.api.models.professional_location_sector import ProfessionalLocationSector


class Sector(Base):
    """Sector model."""

    __tablename__ = "sectors"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid7)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    institution_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("institutions.id"), nullable=True
    )
    created_by: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=text("CURRENT_TIMESTAMP"), nullable=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    institution: Mapped[Institution | None] = relationship("Institution", back_populates="sectors")
    contract_values: Mapped[list["InstitutionContractSectorValue"]] = relationship(
        "InstitutionContractSectorValue", back_populates="sector", cascade="all, delete-orphan"
    )
    professional_bindings: Mapped[list["ProfessionalLocationSector"]] = relationship(
        "ProfessionalLocationSector", back_populates="sector", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Sector(id={self.id}, display_name={self.display_name})>"
