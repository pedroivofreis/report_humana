"""Institution contract schemas."""

from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

import pydantic
from pydantic import BaseModel

from app.api.models.institution_contract import ContractType
from app.api.schemas.sectors import SectorResponse
from app.api.schemas.user import UserSimpleResponse


class InstitutionContractBase(BaseModel):
    institution_id: UUID
    user_id: UUID
    type: ContractType
    contract_value: float | None = pydantic.Field(
        None, description="Value for FIXED_MONTHLY contracts"
    )
    start_date: date
    end_date: date | None = None


class InstitutionContractCreate(InstitutionContractBase):
    pass


class InstitutionContractUpdate(BaseModel):
    institution_id: UUID | None = None
    user_id: UUID | None = None
    type: ContractType | None = None
    contract_value: float | None = None
    start_date: date | None = None
    end_date: date | None = None


from app.api.schemas.complementary_data import MaritalStatusEnum
from app.core.cpf import Cpf
from app.core.phone import Phone


class ContractUserComplementaryData(BaseModel):
    marital_status: MaritalStatusEnum | None = None
    model_config = pydantic.ConfigDict(from_attributes=True)


class InstitutionContractUserResponse(UserSimpleResponse):
    email: str
    phone: Phone | None = None
    cpf: Cpf
    complementary_data: ContractUserComplementaryData | None = None


class InstitutionContractResponse(InstitutionContractBase):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime | None = None
    user: InstitutionContractUserResponse | None = None


class InstitutionContractSimpleResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    institution_id: UUID
    user_id: UUID
    type: ContractType
    contract_value: float | None = None
    start_date: date
    end_date: date | None = None
    created_at: datetime
    updated_at: datetime | None = None


# model_rebuild
InstitutionContractResponse.model_rebuild()
