"""Timesheet models."""

from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid_utils import uuid7

if TYPE_CHECKING:
    from app.api.models.institutions import Institution
    from app.api.models.sectors import Sector
    from app.api.models.user import User
    from app.api.models.user_shifts import UserShift

from app.db.session import Base


class TimesheetStatus(enum.Enum):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    PROCESSING = "PROCESSING"
    IN_ANALYSIS = "IN_ANALYSIS"
    RELEASED = "RELEASED"
    REPROVED = "REPROVED"
    CLOSED = "CLOSED"
    PAID = "PAID"
    OPEN = "OPEN"


class UserTimesheet(Base):

    __tablename__ = "user_timesheets"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid7)
    user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    institution_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("institutions.id"))
    sector_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("sectors.id"))

    competence_date: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[TimesheetStatus] = mapped_column(
        Enum(TimesheetStatus), default=TimesheetStatus.PLANNED
    )

    total_hours_planned: Mapped[float] = mapped_column(Float, default=0.0)
    total_hours_realized: Mapped[float] = mapped_column(Float, default=0.0)
    total_value_planned: Mapped[float] = mapped_column(Float, default=0.0)
    total_value_payable: Mapped[float] = mapped_column(Float, default=0.0)

    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    url: Mapped[str | None] = mapped_column(String, nullable=True)

    shifts: Mapped[list[UserShift]] = relationship("UserShift", back_populates="user_timesheet")
    user: Mapped[User] = relationship("User", foreign_keys=[user_id])
    sector: Mapped[Sector] = relationship("Sector", foreign_keys=[sector_id])
    institution: Mapped[Institution] = relationship("Institution", foreign_keys=[institution_id])

    def __repr__(self) -> str:
        return f"<UserTimesheet(id={self.id}, competence_date={self.competence_date})>"
