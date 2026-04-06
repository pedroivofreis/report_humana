"""Institution service module."""

from uuid import UUID

import structlog
from fastapi import Depends

from app.api.repositories.institutions import InstitutionRepository
from app.api.schemas.institutions import InstitutionRequest, InstitutionResponse
from app.api.services.addresses import AddressService
from app.api.validators.address import AddressValidator
from app.api.validators.institutions import InstitutionValidator
from app.core.exceptions import ResourceNotFoundException

logger = structlog.get_logger(__name__)


class InstitutionService:
    """Institution service."""

    def __init__(
        self,
        repository: InstitutionRepository = Depends(InstitutionRepository),
        address_service: AddressService = Depends(AddressService),
    ):
        self.repository = repository
        self.address_service = address_service

    async def get_institutions(self, include_deleted: bool = False) -> list[InstitutionResponse]:
        """Get all institutions."""
        return await self.repository.get_institutions(include_deleted)

    async def get_institution_by_id(
        self, institution_id: UUID, include_deleted: bool = False
    ) -> InstitutionResponse:
        """Get a institution by id."""
        institution = await self.repository.get_institution_by_id(institution_id, include_deleted)
        if not institution:
            raise ResourceNotFoundException(resource_name="institution", resource_id=institution_id)
        return institution

    async def create_institution(self, institution: InstitutionRequest) -> InstitutionResponse:
        """Create a institution."""
        await InstitutionValidator.validate(institution)

        if institution.address:
            AddressValidator.validate(institution.address)
            address = await self.address_service.create_address(institution.address)
            institution.address_id = address.id

        new_institution = await self.repository.create_institution(institution)

        if institution.address:
            new_institution.address = address
        return new_institution

    async def update_institution(
        self, institution_id: UUID, institutionData: InstitutionRequest
    ) -> InstitutionResponse:
        """Update a institution."""
        institution = await self.get_institution_by_id(institution_id)
        if not institution:
            raise ResourceNotFoundException(resource_name="institution", resource_id=institution_id)

        await InstitutionValidator.validate(institutionData)

        updated = await self.repository.update_institution(institution_id, institutionData)
        return updated

    async def delete_institution(self, institution_id: UUID) -> None:
        """Delete a institution."""
        await self.repository.delete_institution(institution_id)
