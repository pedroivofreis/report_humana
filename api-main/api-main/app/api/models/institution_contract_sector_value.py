"""Institution contract sector value model module."""

from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid_utils import uuid7

from app.db.session import Base

if TYPE_CHECKING:
    from app.api.models.institution_contract import InstitutionContract
    from app.api.models.sectors import Sector


class InstitutionContractSectorValue(Base):
    """Institution contract sector value model."""

    __tablename__ = "institution_contract_sector_values"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid7, index=True)
    institution_contract_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("institution_contracts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sector_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("sectors.id", ondelete="CASCADE"), nullable=False, index=True
    )
    hourly_value: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=text("CURRENT_TIMESTAMP"), nullable=True
    )

    # Relationships
    institution_contract: Mapped["InstitutionContract"] = relationship(
        "InstitutionContract", back_populates="sector_values"
    )
    sector: Mapped["Sector"] = relationship("Sector", back_populates="contract_values")

    def __repr__(self) -> str:
        return f"<InstitutionContractSectorValue(id={self.id}, value={self.hourly_value})>"
