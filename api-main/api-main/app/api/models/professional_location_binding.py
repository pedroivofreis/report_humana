"""Professional Location Binding model module."""

from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, UniqueConstraint, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid_utils import uuid7

from app.db.session import Base

if TYPE_CHECKING:
    from app.api.models.institutions import Institution
    from app.api.models.professional_location_sector import ProfessionalLocationSector
    from app.api.models.user import User


class BindingContractType(str, enum.Enum):
    """Contract type enum."""

    PJ = "PJ"
    CLT = "CLT"


class BindingStatus(str, enum.Enum):
    """Binding status enum."""

    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    CANCELED = "CANCELED"
    TERMINATED = "TERMINATED"


class ProfessionalLocationBinding(Base):
    """Professional Location Binding model."""

    __tablename__ = "professional_location_bindings"
    __table_args__ = (
        UniqueConstraint("user_id", "institution_id", name="uq_professional_location"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid7)
    user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    institution_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    contract_type: Mapped[BindingContractType] = mapped_column(
        Enum(BindingContractType, name="binding_contract_type", native_enum=False), nullable=False
    )
    status: Mapped[BindingStatus] = mapped_column(
        Enum(BindingStatus, name="binding_status", native_enum=False), default=BindingStatus.PENDING, nullable=False
    )
    created_by: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=text("CURRENT_TIMESTAMP"), nullable=True
    )

    user: Mapped[User | None] = relationship("User", back_populates="location_bindings")
    institution: Mapped[Institution | None] = relationship("Institution", back_populates="professional_bindings")
    sectors: Mapped[list[ProfessionalLocationSector]] = relationship(
        "ProfessionalLocationSector", back_populates="binding", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ProfessionalLocationBinding(id={self.id}, user_id={self.user_id}, institution_id={self.institution_id})>"
