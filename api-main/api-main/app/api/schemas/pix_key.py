"""Pix key schema module."""

from datetime import datetime
from enum import Enum
from uuid import UUID

import pydantic


class PixKeyType(str, Enum):
    """Pix key type enum."""

    CPF = "CPF"
    CNPJ = "CNPJ"
    EMAIL = "email"
    PHONE = "phone"
    RANDOM = "random"


class PixKeyResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    type: str
    code: str
    is_active: bool
    is_main: bool
    created_at: datetime
    updated_at: datetime | None = None


class PixKeyCreateRequest(pydantic.BaseModel):
    user_id: UUID = pydantic.Field(..., description="ID do usuário")
    type: PixKeyType = pydantic.Field(
        ..., description="Tipo da chave PIX (CPF, CNPJ, email, phone, random)"
    )
    code: str = pydantic.Field(..., min_length=1, max_length=255, description="Valor da chave PIX")
    is_active: bool = pydantic.Field(default=True, description="Indica se a chave está ativa")
    is_main: bool = pydantic.Field(default=False, description="Indica se é a chave PIX principal")


class PixKeyUpdateRequest(pydantic.BaseModel):
    type: PixKeyType | None = pydantic.Field(
        None, description="Tipo da chave PIX (CPF, CNPJ, email, phone, random)"
    )
    code: str | None = pydantic.Field(
        None, min_length=1, max_length=255, description="Valor da chave PIX"
    )
    is_active: bool | None = pydantic.Field(None, description="Indica se a chave está ativa")
    is_main: bool | None = pydantic.Field(None, description="Indica se é a chave PIX principal")
