from datetime import datetime
from uuid import UUID

import pydantic

from app.api.schemas.address import AddressCreateRequest, AddressResponse
from app.api.schemas.institution_contract import InstitutionContractSimpleResponse
from app.api.schemas.sectors import SectorResponse
from app.core.cnpj import Cnpj


class InstitutionSimpleResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    display_name: str
    social_name: str
    tax_document: Cnpj
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class InstitutionResponse(InstitutionSimpleResponse):
    model_config = pydantic.ConfigDict(from_attributes=True)

    address: AddressResponse | None = None
    sectors: list[SectorResponse] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
    lst_contract: InstitutionContractSimpleResponse | None = None


class InstitutionRequest(pydantic.BaseModel):
    display_name: str
    social_name: str
    tax_document: Cnpj
    is_active: bool = True
    address_id: UUID | None = None
    address: AddressCreateRequest | None = None
