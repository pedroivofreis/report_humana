"""Specialty router module."""

from uuid import UUID

import fastapi
import structlog
from fastapi import Depends, Query

from app.api.schemas.specialty import (
    SpecialtyCreateRequest,
    SpecialtyResponse,
    SpecialtyUpdateRequest,
)
from app.api.services.specialty import SpecialtyService

logger = structlog.get_logger(__name__)

router = fastapi.APIRouter()


@router.get(
    "",
    response_model=list[SpecialtyResponse],
    status_code=200,
    description="Specialty endpoint to get all specialties",
)
async def specialties(
    include_inactive: bool = Query(default=False, description="Include inactive specialties"),
    service: SpecialtyService = Depends(SpecialtyService),
) -> list[SpecialtyResponse]:
    """
    Specialty endpoint to get all specialties.

    Args:
        include_inactive: Include inactive specialties.
        service: Specialty service dependency.

    Returns:
        list[SpecialtyResponse]: List of specialties.
    """
    logger.info("Getting all specialties")
    return await service.get_specialties(include_inactive=include_inactive)


@router.get(
    "/{specialty_id}",
    response_model=SpecialtyResponse,
    status_code=200,
    description="Specialty endpoint to get a specialty by id.",
)
async def specialty_by_id(
    specialty_id: UUID,
    service: SpecialtyService = Depends(SpecialtyService),
) -> SpecialtyResponse | None:
    """
    Specialty endpoint to get a specialty by id.

    Args:
        specialty_id: Specialty id.
        service: Specialty service dependency.

    Returns:
        SpecialtyResponse: Specialty.
    """
    logger.info("Getting specialty by id")
    logger.info(f"Specialty id: {specialty_id}")
    return await service.get_specialty_by_id(specialty_id)


@router.post(
    "",
    response_model=SpecialtyResponse,
    status_code=201,
    description="Specialty endpoint to create a specialty.",
)
async def create_specialty(
    specialty: SpecialtyCreateRequest,
    service: SpecialtyService = Depends(SpecialtyService),
) -> SpecialtyResponse:
    """
    Specialty endpoint to create a specialty.

    Args:
        specialty: Specialty data.
        service: Specialty service dependency.

    Returns:
        SpecialtyResponse: Specialty.
    """
    logger.info("Creating specialty")
    logger.info(f"Specialty: {specialty}")
    return await service.create_specialty(specialty)


@router.put(
    "/{specialty_id}",
    response_model=SpecialtyResponse,
    status_code=200,
    description="Specialty endpoint to update a specialty.",
)
async def update_specialty(
    specialty_id: UUID,
    specialty: SpecialtyUpdateRequest,
    service: SpecialtyService = Depends(SpecialtyService),
) -> SpecialtyResponse:
    """
    Specialty endpoint to update a specialty.

    Args:
        specialty_id: Specialty id.
        specialty: Specialty data.
        service: Specialty service dependency.

    Returns:
        SpecialtyResponse: Specialty.
    """
    logger.info("Updating specialty")
    logger.info(f"Specialty id: {specialty_id}")
    logger.info(f"Specialty: {specialty}")
    return await service.update_specialty(specialty_id, specialty)


@router.delete(
    "/{specialty_id}",
    status_code=204,
    description="Specialty endpoint to delete a specialty.",
)
async def delete_specialty(
    specialty_id: UUID,
    service: SpecialtyService = Depends(SpecialtyService),
) -> None:
    """
    Specialty endpoint to delete a specialty.

    Args:
        specialty_id: Specialty id.
        service: Specialty service dependency.

    Returns:
        None.
    """
    logger.info("Deleting specialty")
    logger.info(f"Specialty id: {specialty_id}")
    return await service.delete_specialty(specialty_id)
