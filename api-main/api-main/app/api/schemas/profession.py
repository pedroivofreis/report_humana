"""Profession schema module."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

import pydantic


class ProfessionResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None


class ProfessionCreateRequest(pydantic.BaseModel):
    name: str = pydantic.Field(..., min_length=1, max_length=255, description="Nome da profissão")
    description: str | None = pydantic.Field(None, description="Descrição da profissão")
    is_active: bool = pydantic.Field(default=True, description="Indica se a profissão está ativa")


class ProfessionUpdateRequest(pydantic.BaseModel):
    name: str | None = pydantic.Field(
        None, min_length=1, max_length=255, description="Nome da profissão"
    )
    description: str | None = pydantic.Field(None, description="Descrição da profissão")
    is_active: bool | None = pydantic.Field(None, description="Indica se a profissão está ativa")

