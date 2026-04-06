"""Institution contract model module."""

import enum
from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid_utils import uuid7

from app.db.session import Base

if TYPE_CHECKING:
    from app.api.models.institutions import Institution
    from app.api.models.user import User


class ContractType(str, enum.Enum):
    """Contract type enum."""

    FIXED_MONTHLY = "FIXED_MONTHLY"
    CONSULTATION_COUNT = "CONSULTATION_COUNT"
    HOURLY_RATE_PER_SECTOR = "HOURLY_RATE_PER_SECTOR"


class InstitutionContract(Base):
    """Institution contract model."""

    __tablename__ = "institution_contracts"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid7, index=True)
    institution_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[ContractType] = mapped_column(
        Enum(ContractType, name="contract_type", native_enum=False), nullable=False
    )
    contract_value: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=text("CURRENT_TIMESTAMP"), nullable=True
    )

    # Relationships
    institution: Mapped["Institution"] = relationship("Institution", back_populates="contracts")
    user: Mapped["User"] = relationship("User", back_populates="institution_contracts")
    sector_values: Mapped[list["InstitutionContractSectorValue"]] = relationship(
        "InstitutionContractSectorValue",
        back_populates="institution_contract",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<InstitutionContract(id={self.id}, type={self.type})>"
