"""Professional CRM service module."""

from uuid import UUID

import structlog
from fastapi import Depends

from app.api.repositories.professional_crm import ProfessionalCrmRepository
from app.api.schemas.professional_crm import (
    ProfessionalCrmCreateRequest,
    ProfessionalCrmResponse,
    ProfessionalCrmUpdateRequest,
)
from app.core.exceptions import NotFoundException

logger = structlog.getLogger(__name__)


class ProfessionalCrmService:
    """Professional CRM service."""

    def __init__(self, repository: ProfessionalCrmRepository = Depends(ProfessionalCrmRepository)):
        self.repository = repository

    async def get_all_professional_crms(self) -> list[ProfessionalCrmResponse]:
        """Get all professional CRMs."""
        logger.debug("Get all professional CRMs")
        return await self.repository.get_all_professional_crms()

    async def get_professional_crm_by_id(
        self, professional_crm_id: UUID
    ) -> ProfessionalCrmResponse:
        """Get a professional CRM by id."""
        logger.debug(f"Get professional CRM by id: {professional_crm_id}")
        professional_crm = await self.repository.get_professional_crm_by_id(professional_crm_id)
        if not professional_crm:
            raise NotFoundException("Professional CRM not found")

        return professional_crm

    async def get_professional_crms_by_user_id(
        self, user_id: UUID
    ) -> list[ProfessionalCrmResponse]:
        """Get all professional CRMs by user id."""
        return await self.repository.get_professional_crms_by_user_id(user_id)

    async def create_professional_crm(
        self, professional_crm: ProfessionalCrmCreateRequest
    ) -> ProfessionalCrmResponse:
        """Create a professional CRM."""
        return await self.repository.create_professional_crm(professional_crm)

    async def update_professional_crm(
        self, professional_crm_id: UUID, professional_crm: ProfessionalCrmUpdateRequest
    ) -> ProfessionalCrmResponse:
        """Update a professional CRM."""

        if await self.repository.get_professional_crm_by_id(professional_crm_id) is None:
            raise NotFoundException("Professional CRM not found")

        return await self.repository.update_professional_crm(professional_crm_id, professional_crm)

    async def delete_professional_crm(self, professional_crm_id: UUID) -> None:
        """Delete a professional CRM."""

        if await self.repository.get_professional_crm_by_id(professional_crm_id) is None:
            raise NotFoundException("Professional CRM not found")

        return await self.repository.delete_professional_crm(professional_crm_id)
