"""User Observation schema module."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

import pydantic


class UserObservationResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    target_user_id: UUID
    owner_id: UUID
    observation: str
    created_at: datetime


class UserObservationCreateRequest(pydantic.BaseModel):
    target_user_id: UUID = pydantic.Field(..., description="ID do usuário a quem a observação foi feita")
    owner_id: UUID = pydantic.Field(..., description="ID do usuário que fez a observação")
    observation: str = pydantic.Field(..., min_length=1, description="Texto da observação")


class OwnerSummary(pydantic.BaseModel):
    """Dados resumidos do autor da observação."""

    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    last_name: str
    profile_picture: str | None = None
    profession: str | None = None


class UserObservationHistoryItem(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    owner: OwnerSummary
    observation: str
    created_at: datetime


class UserObservationHistoryResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    target_user_id: UUID
    total: int
    observations: list[UserObservationHistoryItem]
