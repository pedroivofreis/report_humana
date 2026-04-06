"""Institution router module."""

from uuid import UUID

import fastapi
import structlog
from fastapi import Depends, Query

from app.api.schemas.institutions import InstitutionRequest, InstitutionResponse
from app.api.services.institutions import InstitutionService

logger = structlog.get_logger(__name__)

router = fastapi.APIRouter()


@router.get(
    "",
    response_model=list[InstitutionResponse],
    status_code=200,
    description="Get all institutions",
)
async def get_institutions(
    service: InstitutionService = Depends(),
    include_deleted: bool = Query(
        default=False, description="Include deleted institutions", alias="include_deleted"
    ),
) -> list[InstitutionResponse]:
    """Get all institutions."""
    return await service.get_institutions(include_deleted)


@router.get(
    "/{institution_id}",
    response_model=InstitutionResponse,
    status_code=200,
    description="Get institution by ID",
)
async def get_institution(
    institution_id: UUID,
    service: InstitutionService = Depends(),
    include_deleted: bool = Query(
        default=False, description="Include deleted institutions", alias="include_deleted"
    ),
) -> InstitutionResponse:
    """Get institution by ID."""
    logger.debug("get_institution_endpoint_called", institution_id=institution_id)
    return await service.get_institution_by_id(institution_id, include_deleted)


@router.post(
    "",
    response_model=InstitutionResponse | None,
    status_code=201,
    description="Create a institution",
)
async def create_institution(
    institution: InstitutionRequest,
    service: InstitutionService = Depends(),
) -> InstitutionResponse | None:
    """Create a institution."""
    logger.debug("create_institution_endpoint_called")
    return await service.create_institution(institution)


@router.put(
    "/{institution_id}",
    response_model=InstitutionResponse,
    status_code=200,
    description="Update a institution",
)
async def update_institution(
    institution_id: UUID,
    institution: InstitutionRequest,
    service: InstitutionService = Depends(),
) -> InstitutionResponse:
    """Update a institution."""
    logger.debug("update_institution_endpoint_called", institution_id=institution_id)
    return await service.update_institution(institution_id, institution)


@router.delete(
    "/{institution_id}",
    status_code=204,
    description="Delete a institution",
)
async def delete_institution(
    institution_id: UUID,
    service: InstitutionService = Depends(),
) -> None:
    """Delete a institution."""
    logger.debug("delete_institution_endpoint_called", institution_id=institution_id)
    return await service.delete_institution(institution_id)
