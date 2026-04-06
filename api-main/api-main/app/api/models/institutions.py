from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid_utils import uuid7

from app.core.cnpj import CnpjType
from app.db.session import Base

if TYPE_CHECKING:
    from app.api.models.address import Address
    from app.api.models.sectors import Sector
    from app.api.models.professional_location_binding import ProfessionalLocationBinding


class Institution(Base):
    """Institution model."""

    __tablename__ = "institutions"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid7)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    social_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    tax_document: Mapped[CnpjType] = mapped_column(CnpjType, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    address_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("addresses.id"), nullable=True)
    created_by: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=text("CURRENT_TIMESTAMP"), nullable=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    address: Mapped[Address | None] = relationship("Address", back_populates="institution")
    sectors: Mapped[list[Sector]] = relationship("Sector", back_populates="institution")
    contracts: Mapped[list["InstitutionContract"]] = relationship(
        "InstitutionContract", back_populates="institution", cascade="all, delete-orphan"
    )
    professional_bindings: Mapped[list["ProfessionalLocationBinding"]] = relationship(
        "ProfessionalLocationBinding", back_populates="institution", cascade="all, delete-orphan"
    )

    @property
    def lst_contract(self) -> "InstitutionContract | None":
        """Return the latest contract."""
        if not self.contracts:
            return None
        return max(self.contracts, key=lambda c: (c.start_date, c.created_at))

    def __repr__(self) -> str:
        return f"<Institution(id={self.id}, display_name={self.display_name})>"
