"""Professional CRM schema module."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

import pydantic


class ProfessionalCrmResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    code: str
    state: str
    issue_date: date | None = None
    expiration_date: date | None = None
    validated_at: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None


class ProfessionalCrmCreateRequest(pydantic.BaseModel):
    user_id: UUID = pydantic.Field(..., description="ID do usuário")
    code: str = pydantic.Field(..., min_length=1, max_length=50, description="Código do CRM")
    state: str = pydantic.Field(
        ..., min_length=2, max_length=2, description="UF do CRM (ex: SP, RJ)"
    )
    issue_date: date | None = pydantic.Field(None, description="Data de emissão do CRM")
    expiration_date: date | None = pydantic.Field(None, description="Data de vencimento do CRM")
    validated_at: datetime | None = pydantic.Field(None, description="Data de validação do CRM")


class ProfessionalCrmUpdateRequest(pydantic.BaseModel):
    code: str | None = pydantic.Field(
        None, min_length=1, max_length=50, description="Código do CRM"
    )
    state: str | None = pydantic.Field(
        None, min_length=2, max_length=2, description="UF do CRM (ex: SP, RJ)"
    )
    issue_date: date | None = pydantic.Field(None, description="Data de emissão do CRM")
    expiration_date: date | None = pydantic.Field(None, description="Data de vencimento do CRM")
    validated_at: datetime | None = pydantic.Field(None, description="Data de validação do CRM")
