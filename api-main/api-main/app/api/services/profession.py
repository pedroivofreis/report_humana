"""Profession service module."""

from uuid import UUID

import structlog
from fastapi import Depends

from app.api.repositories.profession import ProfessionRepository
from app.api.schemas.profession import (
    ProfessionCreateRequest,
    ProfessionResponse,
    ProfessionUpdateRequest,
)
from app.core.exceptions import NotFoundException

logger = structlog.getLogger(__name__)


class ProfessionService:
    """Profession service."""

    def __init__(self, repository: ProfessionRepository = Depends(ProfessionRepository)):
        self.repository = repository

    async def get_professions(self, include_inactive: bool = False) -> list[ProfessionResponse]:
        """Get all professions."""
        logger.debug("Get all professions")
        return await self.repository.get_professions(include_inactive=include_inactive)

    async def get_profession_by_id(
        self, profession_id: UUID
    ) -> ProfessionResponse | None:
        """Get a profession by id."""
        logger.debug(f"Get profession by id: {profession_id}")
        profession = await self.repository.get_profession_by_id(profession_id)
        if not profession:
            raise NotFoundException("Profession not found")

        return profession

    async def create_profession(self, profession: ProfessionCreateRequest) -> ProfessionResponse:
        """Create a profession."""
        logger.debug("Create profession service")
        return await self.repository.create_profession(profession)

    async def update_profession(
        self, profession_id: UUID, profession: ProfessionUpdateRequest
    ) -> ProfessionResponse:
        """Update a profession."""
        logger.debug(f"Update profession by id: {profession_id}")

        if await self.repository.get_profession_by_id(profession_id) is None:
            raise NotFoundException("Profession not found")

        return await self.repository.update_profession(profession_id, profession)

    async def delete_profession(self, profession_id: UUID) -> None:
        """Delete a profession."""
        logger.debug(f"Delete profession by id: {profession_id}")

        if await self.repository.get_profession_by_id(profession_id) is None:
            raise NotFoundException("Profession not found")

        return await self.repository.delete_profession(profession_id)
