"""User Shift schemas."""

from datetime import date, datetime
from enum import Enum
from uuid import UUID

import pydantic
from pydantic import BaseModel

from app.api.models.user_shifts import ShiftExchangeStatusEnum, ShiftStatus
from app.api.schemas.shifts import ShiftSimpleResponse, ShiftSlotConfigResponse
from app.api.schemas.user import UserSimpleResponse


class AssignmentStrategy(str, Enum):
    EVERY_DAY = "every_day"
    ALTERNATING_DAYS = "alternating_days"
    WORK_12_REST_36 = "12x36"


class BulkAssignRequest(BaseModel):
    user_id: UUID
    shift_id: UUID
    shift_type_id: UUID
    sector_id: UUID
    start_date: date
    end_date: date
    strategy: AssignmentStrategy


class ShiftExchangeResponse(BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    target_user_id: UUID | None
    target_user: UserSimpleResponse | None = None
    old_person_id: UUID | None = None
    old_person: UserSimpleResponse | None = None
    requested_at: datetime
    status: ShiftExchangeStatusEnum
    manager_notes: str | None = None


class ShiftExchangeCreate(BaseModel):
    target_user_id: UUID | None
    manager_notes: str | None = None


class UserShiftBase(BaseModel):
    date: date
    planned_start: datetime | None = None
    planned_end: datetime | None = None
    agreed_value: float
    status: ShiftStatus
    weight: float = 1.0
    notes: str | None = None
    needs_assistance: bool | None = None
    assistance_reason: str | None = None
    assistance_user_id: UUID | None = None


class UserShiftCreate(UserShiftBase):
    shift_id: UUID
    user_id: UUID | None = None


class UserShiftUpdate(BaseModel):
    user_id: UUID | None = None
    checkin_time: datetime | None = None
    checkout_time: datetime | None = None
    checkin_lat: float | None = None
    checkin_long: float | None = None
    status: ShiftStatus | None = None
    agreed_value: float | None = None
    notes: str | None = None
    needs_assistance: bool | None = None
    assistance_reason: str | None = None
    assistance_user_id: UUID | None = None
    is_fixed_professional: bool | None = None
    shift_exchange: ShiftExchangeCreate | None = None


class UserShiftResponse(UserShiftBase):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    user_timesheet_id: UUID | None = None
    shift_id: UUID
    user_id: UUID | None
    user: UserSimpleResponse | None = None
    planned_start: datetime
    planned_end: datetime
    checkin_time: datetime | None
    checkout_time: datetime | None
    checkin_lat: float | None
    checkin_long: float | None
    hours_worked: float
    final_value: float
    needs_assistance: bool | None = None
    assistance_reason: str | None = None
    assistance_user: UserSimpleResponse | None = None


class UserShiftDetailResponse(UserShiftResponse):
    shift: ShiftSimpleResponse | None = None
    slot_config: ShiftSlotConfigResponse | None = None
    shift_exchanges: list[ShiftExchangeResponse] = []


class SectorSimpleResponse(BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    display_name: str


class UserShiftsBySectorResponse(BaseModel):
    sector: SectorSimpleResponse
    shifts: list[UserShiftResponse]
