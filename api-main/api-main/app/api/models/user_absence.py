"""User Absence models."""

from __future__ import annotations

import enum
from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Date, Enum, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid_utils import uuid7

if TYPE_CHECKING:
    from app.api.models.sectors import Sector
    from app.api.models.user import User

from app.db.session import Base


class AbsenceTypeEnum(enum.Enum):
    HOLIDAY = "HOLIDAY"
    VACATION = "VACATION"
    TIME_OFF = "TIME_OFF"
    LICENSE = "LICENSE"
    EXCHANGE = "EXCHANGE"


class UserAbsence(Base):
    __tablename__ = "user_absences"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid7)
    user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True, nullable=False)
    sector_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("sectors.id"), nullable=True)

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    type: Mapped[AbsenceTypeEnum] = mapped_column(Enum(AbsenceTypeEnum), nullable=False)
    reason: Mapped[str | None] = mapped_column(String, nullable=True)

    user: Mapped[User] = relationship("User", back_populates="absences")
    sector: Mapped[Sector | None] = relationship("Sector")

    def __repr__(self) -> str:
        return f"<UserAbsence(id={self.id}, user_id={self.user_id}, type={self.type})>"
