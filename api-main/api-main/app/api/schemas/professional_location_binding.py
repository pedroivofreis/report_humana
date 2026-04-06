"""Professional Location Binding schemas module."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.api.models.professional_location_binding import BindingContractType, BindingStatus
from app.api.schemas.attachment import AttachmentResponse
from app.api.schemas.institutions import InstitutionSimpleResponse
from app.api.schemas.sectors import SectorResponse


class ProfessionalLocationSectorResponse(BaseModel):
    """Professional Location Sector response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sector_id: UUID
    sector: SectorResponse | None = None


class ProfessionalLocationBindingBase(BaseModel):
    """Base schema for Professional Location Binding."""

    contract_type: BindingContractType
    status: BindingStatus = BindingStatus.PENDING


class ProfessionalLocationBindingCreate(ProfessionalLocationBindingBase):
    """Schema for creating a Professional Location Binding."""

    user_id: UUID
    institution_id: UUID
    sector_ids: list[UUID] = Field(min_length=1)


class ProfessionalLocationBindingUpdate(BaseModel):
    """Schema for updating a Professional Location Binding."""

    contract_type: BindingContractType | None = None
    status: BindingStatus | None = None
    sector_ids: list[UUID] | None = Field(None, min_length=1)


class ProfessionalLocationBindingResponse(ProfessionalLocationBindingBase):
    """Response schema for Professional Location Binding."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    institution_id: UUID
    sectors: list[ProfessionalLocationSectorResponse] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None
    institution: InstitutionSimpleResponse | None = None
    contract_attachment: AttachmentResponse | None = None
