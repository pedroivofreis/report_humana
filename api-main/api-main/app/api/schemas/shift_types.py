"""Shift Type schemas."""

from datetime import datetime
from uuid import UUID

import pydantic
from pydantic import BaseModel


class ShiftTypeBase(BaseModel):
    institution_id: UUID
    name: str
    active: bool = True


class ShiftTypeCreate(ShiftTypeBase):
    pass


class ShiftTypeUpdate(BaseModel):
    institution_id: UUID | None = None
    name: str | None = None
    active: bool | None = None


class ShiftTypeResponse(ShiftTypeBase):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
