"""Sector router module."""

from uuid import UUID

import fastapi
import structlog
from fastapi import Depends, Query

from app.api.schemas.sectors import SectorRequest, SectorResponse
from app.api.services.sectors import SectorService
from app.core.exceptions import ResourceNotFoundException

logger = structlog.get_logger(__name__)

router = fastapi.APIRouter()


@router.get(
    "",
    response_model=list[SectorResponse],
    status_code=200,
    description="Get all sectors",
)
async def get_sectors(
    service: SectorService = Depends(),
    include_deleted: bool = Query(
        default=False, description="Include deleted sectors", alias="include_deleted"
    ),
) -> list[SectorResponse]:
    """Get all sectors."""
    return await service.get_sectors(include_deleted)


@router.get(
    "/{sector_id}",
    response_model=SectorResponse,
    status_code=200,
    description="Get sector by ID",
)
async def get_sector(
    sector_id: UUID,
    service: SectorService = Depends(),
    include_deleted: bool = Query(
        default=False, description="Include deleted sectors", alias="include_deleted"
    ),
) -> SectorResponse:
    """Get sector by ID."""
    sector = await service.get_sector_by_id(sector_id, include_deleted)
    if not sector:
        raise ResourceNotFoundException(resource_name="sector", resource_id=sector_id)
    return sector


@router.post(
    "",
    response_model=SectorResponse | None,
    status_code=201,
    description="Create a sector",
)
async def create_sector(
    sector: SectorRequest,
    service: SectorService = Depends(),
) -> SectorResponse | None:
    """Create a sector."""
    return await service.create_sector(sector)


@router.put(
    "/{sector_id}",
    response_model=SectorResponse,
    status_code=200,
    description="Update a sector",
)
async def update_sector(
    sector_id: UUID,
    sector: SectorRequest,
    service: SectorService = Depends(),
) -> SectorResponse:
    """Update a sector."""
    return await service.update_sector(sector_id, sector)


@router.delete(
    "/{sector_id}",
    status_code=204,
    description="Delete a sector",
)
async def delete_sector(
    sector_id: UUID,
    service: SectorService = Depends(),
) -> None:
    """Delete a sector."""
    return await service.delete_sector(sector_id)
