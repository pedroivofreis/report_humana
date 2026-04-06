"""Professional Location Sector model module."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid_utils import uuid7

from app.db.session import Base

if TYPE_CHECKING:
    from app.api.models.professional_location_binding import ProfessionalLocationBinding
    from app.api.models.sectors import Sector


class ProfessionalLocationSector(Base):
    """Professional Location Sector association model."""

    __tablename__ = "professional_location_sectors"
    __table_args__ = (
        UniqueConstraint("binding_id", "sector_id", name="uq_professional_binding_sector"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid7)
    binding_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("professional_location_bindings.id", ondelete="CASCADE"), nullable=False, index=True)
    sector_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("sectors.id", ondelete="CASCADE"), nullable=False, index=True)

    binding: Mapped[ProfessionalLocationBinding | None] = relationship("ProfessionalLocationBinding", back_populates="sectors")
    sector: Mapped[Sector | None] = relationship("Sector", back_populates="professional_bindings")

    def __repr__(self) -> str:
        return f"<ProfessionalLocationSector(id={self.id}, binding_id={self.binding_id}, sector_id={self.sector_id})>"
