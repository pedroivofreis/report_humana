"""User specialty schema module."""

from datetime import datetime
from uuid import UUID

import pydantic

from app.api.schemas.specialty import SpecialtyResponse


class UserSpecialtyResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    specialty_id: UUID
    is_primary: bool
    created_at: datetime
    updated_at: datetime | None = None


class UserSpecialtyWithDetailsResponse(UserSpecialtyResponse):
    model_config = pydantic.ConfigDict(from_attributes=True)

    specialty: SpecialtyResponse | None = None


class UserSpecialtyCreateRequest(pydantic.BaseModel):
    user_id: UUID = pydantic.Field(..., description="ID do usuário")
    specialty_id: UUID = pydantic.Field(..., description="ID da especialidade")
    is_primary: bool = pydantic.Field(
        default=False, description="Indica se é a especialidade principal"
    )


class UserSpecialtyCreateForUserRequest(pydantic.BaseModel):
    """Payload para criar especialidade junto com o usuário (sem user_id)."""

    specialty_id: UUID = pydantic.Field(..., description="ID da especialidade")
    is_primary: bool = pydantic.Field(
        default=False, description="Indica se é a especialidade principal"
    )


class UserSpecialtyUpdateRequest(pydantic.BaseModel):
    specialty_id: UUID | None = pydantic.Field(None, description="ID da especialidade")
    is_primary: bool | None = pydantic.Field(
        None, description="Indica se é a especialidade principal"
    )
