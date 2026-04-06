"""Institution repository."""

import logging
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.models.sectors import Sector
from app.api.repositories.base import BaseRepository
from app.api.schemas.sectors import SectorRequest, SectorResponse
from app.core.exceptions import ResourceNotFoundException
from app.db.session import AsyncSession, get_db_session

logger = logging.getLogger(__name__)


class SectorRepository(BaseRepository[Sector]):
    """Sector repository."""

    def __init__(self, db: AsyncSession = Depends(get_db_session)):
        super().__init__(model=Sector, db=db)

    async def _get_sector_with_contract_values(self, sector_id: UUID) -> Sector | None:
        """Fetch a sector with contract_values eagerly loaded."""
        query = (
            select(Sector)
            .options(selectinload(Sector.contract_values))
            .where(Sector.id == sector_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_sectors(self, include_deleted: bool = False) -> list[SectorResponse]:
        """Get all sectors."""
        query = select(Sector).options(selectinload(Sector.contract_values))
        if not include_deleted:
            query = query.where(Sector.deleted_at.is_(None))
        result = await self.db.execute(query)
        sectors = result.scalars().all()
        return [SectorResponse.model_validate(sector) for sector in sectors]

    async def get_sector_by_id(
        self, sector_id: UUID, include_deleted: bool = False
    ) -> SectorResponse | None:
        """Get a sector by id."""
        sector = await self._get_sector_with_contract_values(sector_id)
        return SectorResponse.model_validate(sector) if sector else None

    async def create_sector(self, sector: SectorRequest) -> SectorResponse:
        """Create a sector."""
        new_sector = Sector(**sector.model_dump(exclude={"institution"}))
        self.db.add(new_sector)
        await self.db.flush()
        # Re-fetch with eager load to avoid lazy-load MissingGreenlet
        created = await self._get_sector_with_contract_values(new_sector.id)
        return SectorResponse.model_validate(created)

    async def update_sector(self, sector_id: UUID, sectorData: SectorRequest) -> SectorResponse:
        """Update a sector."""
        sector = await self.get_by_id(sector_id)
        if not sector:
            raise ResourceNotFoundException(resource_name="sector", resource_id=sector_id)
        for key, value in sectorData.model_dump(exclude={"institution"}).items():
            setattr(sector, key, value)

        await self.db.commit()
        updated = await self._get_sector_with_contract_values(sector_id)
        return SectorResponse.model_validate(updated)

    async def delete_sector(self, sector_id: UUID) -> None:
        """Soft delete a sector."""
        sector = await self.get_by_id(sector_id)
        if not sector:
            raise ResourceNotFoundException(resource_name="sector", resource_id=sector_id)
        await self.delete(sector_id)
