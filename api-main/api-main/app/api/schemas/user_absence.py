"""User Absence schemas."""

from __future__ import annotations

from datetime import date
from uuid import UUID

import pydantic

from app.api.models.user_absence import AbsenceTypeEnum
from app.api.schemas.user import UserSimpleResponse


class UserAbsenceBase(pydantic.BaseModel):
    user_id: UUID
    sector_id: UUID | None = None
    start_date: date
    end_date: date
    type: AbsenceTypeEnum
    reason: str | None = None

    model_config = pydantic.ConfigDict(from_attributes=True)


class UserAbsenceCreate(UserAbsenceBase):
    pass


class UserAbsenceResponse(UserAbsenceBase):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    user: UserSimpleResponse | None = None
