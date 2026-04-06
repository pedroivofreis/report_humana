"""Institution contract sector value schemas module."""

from datetime import date, datetime
from uuid import UUID

import pydantic
from pydantic import BaseModel

from app.api.schemas.sectors import SectorResponse


class InstitutionContractSectorValueBase(BaseModel):
    institution_contract_id: UUID
    sector_id: UUID
    hourly_value: float


class InstitutionContractSectorValueCreate(BaseModel):
    """Schema to create a sector hourly value. Uses the contract dates automatically."""

    sector_id: UUID
    hourly_value: float


class InstitutionContractSectorValueResponse(InstitutionContractSectorValueBase):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    start_date: date
    end_date: date | None = None
    created_at: datetime
    updated_at: datetime | None = None

    sector: SectorResponse | None = None
