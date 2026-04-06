"""Address schema module."""

from datetime import datetime
from uuid import UUID

import pydantic


class AddressResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID | None = None
    zip_code: str
    street: str
    number: str
    complement: str | None = None
    neighborhood: str
    city: str
    uf: str
    created_at: datetime
    updated_at: datetime | None = None


class AddressCreateRequest(pydantic.BaseModel):
    user_id: UUID | None = None
    zip_code: str = pydantic.Field(
        ..., min_length=8, max_length=10, description="CEP formatted or unformatted"
    )
    street: str = pydantic.Field(..., min_length=1, max_length=255)
    number: str = pydantic.Field(..., min_length=1, max_length=25)
    complement: str | None = pydantic.Field(None, max_length=255)
    neighborhood: str = pydantic.Field(..., min_length=1, max_length=255)
    city: str = pydantic.Field(..., min_length=1, max_length=255)
    uf: str = pydantic.Field(..., min_length=2, max_length=2, description="Estado (UF)")


class AddressUpdateRequest(pydantic.BaseModel):
    user_id: UUID | None = None
    zip_code: str | None = pydantic.Field(
        None, min_length=8, max_length=10, description="CEP formatted or unformatted"
    )
    street: str | None = pydantic.Field(None, min_length=1, max_length=255)
    number: str | None = pydantic.Field(None, min_length=1, max_length=25)
    complement: str | None = pydantic.Field(None, max_length=255)
    neighborhood: str | None = pydantic.Field(None, min_length=1, max_length=255)
    city: str | None = pydantic.Field(None, min_length=1, max_length=255)
    uf: str | None = pydantic.Field(None, min_length=2, max_length=2, description="Estado (UF)")
