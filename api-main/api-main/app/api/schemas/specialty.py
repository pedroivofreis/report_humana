"""Specialty schema module."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

import pydantic


class SpecialtyResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    code: str | None = None
    name: str
    description: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None


class SpecialtyCreateRequest(pydantic.BaseModel):
    code: str | None = pydantic.Field(None, description="Código da especialidade")
    name: str = pydantic.Field(
        ..., min_length=1, max_length=255, description="Nome da especialidade"
    )
    description: str | None = pydantic.Field(None, description="Descrição da especialidade")
    is_active: bool = pydantic.Field(
        default=True, description="Indica se a especialidade está ativa"
    )


class SpecialtyUpdateRequest(pydantic.BaseModel):
    code: str | None = pydantic.Field(None, description="Código da especialidade")
    name: str | None = pydantic.Field(
        None, min_length=1, max_length=255, description="Nome da especialidade"
    )
    description: str | None = pydantic.Field(None, description="Descrição da especialidade")
    is_active: bool | None = pydantic.Field(
        None, description="Indica se a especialidade está ativa"
    )



