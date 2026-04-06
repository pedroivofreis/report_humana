"""Shift Template models."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import JSON, Boolean, Date, Float, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid_utils import uuid7

if TYPE_CHECKING:
    from app.api.models.institutions import Institution
    from app.api.models.sectors import Sector
    from app.api.models.shift_types import ShiftType

from app.db.session import Base


class Shift(Base):

    __tablename__ = "shifts"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid7)
    institution_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("institutions.id"), index=True)
    sector_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("sectors.id"), index=True)

    name: Mapped[str] = mapped_column(String, nullable=False)
    shift_type_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("shift_types.id"), nullable=False)
    shift_type: Mapped[ShiftType] = relationship("ShiftType", lazy="selectin")

    start_time: Mapped[str] = mapped_column(String, nullable=False)
    end_time: Mapped[str] = mapped_column(String, nullable=False)
    duration_hours: Mapped[float] = mapped_column(Float, nullable=False)

    base_value: Mapped[float] = mapped_column(Float, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    allow_flexible_hours: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_geolocation: Mapped[bool] = mapped_column(Boolean, default=True)

    shift_weight: Mapped[float] = mapped_column(Float, default=1.0)

    doctor_group: Mapped[str] = mapped_column(String, nullable=True)
    vacancy_count: Mapped[int] = mapped_column(Integer, nullable=True)
    days_of_week: Mapped[list[int]] = mapped_column(JSON, nullable=True)  # Ex: [0, 2, 4]
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    additional_hourly_rate: Mapped[float] = mapped_column(Float, nullable=True)
    weekend_hourly_rate: Mapped[float] = mapped_column(Float, nullable=True)

    slots: Mapped[list[ShiftSlotConfig]] = relationship(
        "ShiftSlotConfig",
        back_populates="shift",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    institution: Mapped[Institution] = relationship(
        "Institution", lazy="selectin", foreign_keys=[institution_id]
    )

    sector: Mapped[Sector] = relationship("Sector", lazy="selectin", foreign_keys=[sector_id])

    def __repr__(self) -> str:

        return f"<Shift(id={self.id}, name={self.name})>"


class ShiftSlotConfig(Base):
    """
    Configuração específica para cada 'vaga' do template.
    Permite definir usuário fixo por vaga.
    """

    __tablename__ = "shift_slot_configs"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid7)
    shift_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("shifts.id"))
    slot_index: Mapped[int] = mapped_column(Integer, nullable=False)  # 0, 1, 2...

    fixed_user_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    is_fixed: Mapped[bool] = mapped_column(Boolean, default=False)

    shift: Mapped[Shift] = relationship("Shift", back_populates="slots")

    def __repr__(self) -> str:
        return f"<ShiftSlotConfig(id={self.id}, shift={self.shift_id}, slot={self.slot_index})>"
