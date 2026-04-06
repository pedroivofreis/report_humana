"""Specialty service module."""

from uuid import UUID

import structlog
from fastapi import Depends

from app.api.repositories.specialty import SpecialtyRepository
from app.api.schemas.specialty import (
    SpecialtyCreateRequest,
    SpecialtyResponse,
    SpecialtyUpdateRequest,
)
from app.core.exceptions import NotFoundException

logger = structlog.getLogger(__name__)


class SpecialtyService:
    """Specialty service."""

    def __init__(self, repository: SpecialtyRepository = Depends(SpecialtyRepository)):
        self.repository = repository

    async def get_specialties(
        self, include_inactive: bool = False
    ) -> list[SpecialtyResponse]:
        """Get all specialties."""
        logger.debug("Get all specialties")
        return await self.repository.get_specialties(
            include_inactive=include_inactive
        )

    async def get_specialty_by_id(
        self, specialty_id: UUID
    ) -> SpecialtyResponse | None:
        """Get a specialty by id."""
        logger.debug(f"Get specialty by id: {specialty_id}")
        specialty = await self.repository.get_specialty_by_id(specialty_id)
        if not specialty:
            raise NotFoundException("Specialty not found")

        return specialty

    async def create_specialty(self, specialty: SpecialtyCreateRequest) -> SpecialtyResponse:
        """Create a specialty."""
        logger.debug("Create specialty service")
        return await self.repository.create_specialty(specialty)

    async def update_specialty(
        self, specialty_id: UUID, specialty: SpecialtyUpdateRequest
    ) -> SpecialtyResponse:
        """Update a specialty."""
        logger.debug(f"Update specialty by id: {specialty_id}")

        if await self.repository.get_specialty_by_id(specialty_id) is None:
            raise NotFoundException("Specialty not found")

        return await self.repository.update_specialty(specialty_id, specialty)

    async def delete_specialty(self, specialty_id: UUID) -> None:
        """Delete a specialty."""
        logger.debug(f"Delete specialty by id: {specialty_id}")

        if await self.repository.get_specialty_by_id(specialty_id) is None:
            raise NotFoundException("Specialty not found")

        return await self.repository.delete_specialty(specialty_id)
