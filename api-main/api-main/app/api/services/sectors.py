"""Sector service module."""

from uuid import UUID

import structlog
from fastapi import Depends

from app.api.repositories.sectors import SectorRepository
from app.api.repositories.user_shift_repository import UserShiftRepository
from app.api.schemas.sectors import SectorRequest, SectorResponse
from app.core.exceptions import BadRequestException, ResourceNotFoundException

logger = structlog.get_logger(__name__)


class SectorService:
    """Sector service."""

    def __init__(
        self,
        repository: SectorRepository = Depends(SectorRepository),
        user_shift_repository: UserShiftRepository = Depends(UserShiftRepository),
    ):
        self.repository = repository
        self.user_shift_repository = user_shift_repository

    async def get_sectors(self, include_deleted: bool = False) -> list[SectorResponse]:
        """Get all sectors."""
        return await self.repository.get_sectors(include_deleted)

    async def get_sector_by_id(
        self, sector_id: UUID, include_deleted: bool = False
    ) -> SectorResponse | None:
        """Get a sector by id."""
        sector = await self.repository.get_sector_by_id(sector_id, include_deleted)
        if not sector:
            raise ResourceNotFoundException(resource_name="sector", resource_id=sector_id)
        return sector

    async def create_sector(self, sector: SectorRequest) -> SectorResponse:
        """Create a sector."""
        return await self.repository.create_sector(sector)

    async def update_sector(self, sector_id: UUID, sectorData: SectorRequest) -> SectorResponse:
        """Update a sector."""
        sector = await self.get_sector_by_id(sector_id)
        if not sector:
            raise ResourceNotFoundException(resource_name="sector", resource_id=sector_id)

        updated = await self.repository.update_sector(sector_id, sectorData)
        return updated

    async def delete_sector(self, sector_id: UUID) -> None:
        """Delete a sector."""
        has_active_shifts = await self.user_shift_repository.has_active_shifts_for_sector(sector_id)
        if has_active_shifts:
            raise BadRequestException(
                "Não é possível excluir o setor pois ele possui plantões ativos."
            )
        return await self.repository.delete_sector(sector_id)
