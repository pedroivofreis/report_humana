"""User Shift models."""

from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, Date, DateTime, Enum, Float, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid_utils import uuid7

if TYPE_CHECKING:
    from app.api.models.shifts import Shift, ShiftSlotConfig
    from app.api.models.user import User
    from app.api.models.user_timesheets import UserTimesheet

from app.db.session import Base


class ShiftStatus(str, enum.Enum):
    OPEN = "OPEN"
    PLANNED = "PLANNED"
    CONFIRMED = "CONFIRMED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    MISSED = "MISSED"
    SWAPPED = "SWAPPED"
    CANCELED = "CANCELED"


class ShiftExchangeStatusEnum(str, enum.Enum):
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class UserShift(Base):
    __tablename__ = "user_shifts"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid7)
    user_timesheet_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("user_timesheets.id"))
    shift_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("shifts.id"))
    user_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id"), index=True, nullable=True
    )

    date: Mapped[datetime] = mapped_column(Date, nullable=False)
    competence_date: Mapped[str] = mapped_column(String, nullable=False, index=True)

    planned_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    planned_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    agreed_value: Mapped[float] = mapped_column(Float, nullable=False)

    checkin_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    checkout_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    checkin_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    checkin_long: Mapped[float | None] = mapped_column(Float, nullable=True)

    status: Mapped[ShiftStatus] = mapped_column(Enum(ShiftStatus), default=ShiftStatus.PLANNED)

    needs_assistance: Mapped[bool] = mapped_column(Boolean, default=False)
    assistance_reason: Mapped[str | None] = mapped_column(String, nullable=True)

    weight: Mapped[float] = mapped_column(Float, default=1.0)

    hours_worked: Mapped[float] = mapped_column(Float, default=0.0)
    final_value: Mapped[float] = mapped_column(Float, default=0.0)

    notes: Mapped[str | None] = mapped_column(String, nullable=True)

    user_timesheet: Mapped[UserTimesheet] = relationship("UserTimesheet", back_populates="shifts")
    exchanges: Mapped[list[ShiftExchange]] = relationship(
        "ShiftExchange", back_populates="requester_shift"
    )
    shift: Mapped[Shift] = relationship("Shift", foreign_keys=[shift_id])
    user: Mapped[User | None] = relationship("User", foreign_keys=[user_id])
    assistance_user_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=True
    )
    assistance_user: Mapped[User | None] = relationship("User", foreign_keys=[assistance_user_id])

    slot_config_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("shift_slot_configs.id"), nullable=True
    )
    slot_config: Mapped[ShiftSlotConfig | None] = relationship("ShiftSlotConfig")

    def __repr__(self) -> str:
        return f"<UserShift(id={self.id}, date={self.date})>"


class ShiftExchange(Base):
    """Armazena quem pediu, quem aceitou e se o gestor aprovou."""

    __tablename__ = "shift_exchanges"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid7)
    requester_shift_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("user_shifts.id"))
    target_user_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("users.id"), nullable=True)
    old_person_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("users.id"), nullable=True)

    requested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    status: Mapped[ShiftExchangeStatusEnum] = mapped_column(
        Enum(ShiftExchangeStatusEnum), default=ShiftExchangeStatusEnum.PENDING_APPROVAL
    )
    manager_notes: Mapped[str | None] = mapped_column(String, nullable=True)

    requester_shift: Mapped[UserShift] = relationship("UserShift", back_populates="exchanges")
    target_user: Mapped[User | None] = relationship("User", foreign_keys=[target_user_id])
    old_person: Mapped[User | None] = relationship("User", foreign_keys=[old_person_id])

    def __repr__(self) -> str:
        return f"<ShiftExchange(id={self.id}, requester_shift_id={self.requester_shift_id})>"
