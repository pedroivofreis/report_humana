"""Bank account schema module."""

from datetime import datetime
from uuid import UUID

import pydantic


class BankAccountResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    bank_code: str
    bank_name: str
    agency: str
    account_number: str
    account_digit: str
    account_type: str
    is_main: bool
    created_at: datetime
    updated_at: datetime | None = None


class BankAccountCreateRequest(pydantic.BaseModel):
    user_id: UUID
    bank_code: str = pydantic.Field(..., min_length=1, max_length=10, description="Código do banco")
    bank_name: str = pydantic.Field(..., min_length=1, max_length=255, description="Nome do banco")
    agency: str = pydantic.Field(..., min_length=1, max_length=10, description="Agência")
    account_number: str = pydantic.Field(
        ..., min_length=1, max_length=20, description="Número da conta"
    )
    account_digit: str = pydantic.Field(
        ..., min_length=1, max_length=2, description="Dígito da conta"
    )
    account_type: str = pydantic.Field(
        ..., min_length=1, max_length=20, description="Tipo da conta (checking, savings, etc)"
    )
    is_main: bool = pydantic.Field(default=False, description="Indica se é a conta principal")


class BankAccountUpdateRequest(pydantic.BaseModel):
    bank_code: str | None = pydantic.Field(
        None, min_length=1, max_length=10, description="Código do banco"
    )
    bank_name: str | None = pydantic.Field(
        None, min_length=1, max_length=255, description="Nome do banco"
    )
    agency: str | None = pydantic.Field(None, min_length=1, max_length=10, description="Agência")
    account_number: str | None = pydantic.Field(
        None, min_length=1, max_length=20, description="Número da conta"
    )
    account_digit: str | None = pydantic.Field(
        None, min_length=1, max_length=2, description="Dígito da conta"
    )
    account_type: str | None = pydantic.Field(
        None, min_length=1, max_length=20, description="Tipo da conta (checking, savings, etc)"
    )
    is_main: bool | None = pydantic.Field(None, description="Indica se é a conta principal")
