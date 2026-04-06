"""Shift Type models."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid_utils import uuid7

from app.db.session import Base


class ShiftType(Base):
    """
    Tipo de Plantão.
    Ex: Diurno, Noturno, 12h, 24h, etc.
    """

    __tablename__ = "shift_types"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid7)
    institution_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    institution = relationship("Institution")

    def __repr__(self) -> str:
        return f"<ShiftType(id={self.id}, name={self.name})>"
