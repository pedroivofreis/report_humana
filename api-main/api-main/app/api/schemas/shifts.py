"""Shift schemas."""

from datetime import date
from uuid import UUID

import pydantic
from pydantic import BaseModel, computed_field

from app.api.schemas.shift_types import ShiftTypeResponse


class ShiftSlotConfigBase(BaseModel):
    slot_index: int
    fixed_user_id: UUID | None = None
    is_fixed: bool = False


class ShiftSlotConfigCreate(ShiftSlotConfigBase):
    pass


class ShiftSlotConfigUpdate(ShiftSlotConfigBase):
    pass


class ShiftSlotConfigResponse(ShiftSlotConfigBase):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    shift_id: UUID


class ShiftBase(BaseModel):
    name: str
    shift_type_id: UUID
    start_time: str
    duration_hours: float
    base_value: float
    is_active: bool = True
    allow_flexible_hours: bool = False
    requires_geolocation: bool = True
    doctor_group: str | None = None
    vacancy_count: int | None = None
    days_of_week: list[int] | None = None
    start_date: date
    end_date: date
    additional_hourly_rate: float | None = None
    weekend_hourly_rate: float | None = None


class ShiftCreate(ShiftBase):
    institution_id: UUID
    sector_id: UUID
    end_time: str | None = None
    shift_weight: float | None = None


class ShiftUpdate(ShiftBase):
    end_time: str | None = None
    shift_weight: float | None = None
    slots: list[ShiftSlotConfigUpdate] | None = None


class ShiftResponse(ShiftBase):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    institution_id: UUID
    sector_id: UUID
    shift_type: ShiftTypeResponse | None = None
    slots: list[ShiftSlotConfigResponse] = []
    end_time: str
    shift_weight: float

    @computed_field
    @property
    def days_of_week_display(self) -> list[str] | None:
        if self.days_of_week is None:
            return None

        days_map = {
            0: "Domingo",
            1: "Segunda-feira",
            2: "Terça-feira",
            3: "Quarta-feira",
            4: "Quinta-feira",
            5: "Sexta-feira",
            6: "Sábado",
        }
        return [days_map.get(day, "") for day in self.days_of_week]


class ShiftSimpleResponse(ShiftBase):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    institution_id: UUID
    sector_id: UUID
    end_time: str
    shift_weight: float

    @computed_field
    @property
    def days_of_week_display(self) -> list[str] | None:
        if self.days_of_week is None:
            return None

        days_map = {
            0: "Domingo",
            1: "Segunda-feira",
            2: "Terça-feira",
            3: "Quarta-feira",
            4: "Quinta-feira",
            5: "Sexta-feira",
            6: "Sábado",
        }
        return [days_map.get(day, "") for day in self.days_of_week]
