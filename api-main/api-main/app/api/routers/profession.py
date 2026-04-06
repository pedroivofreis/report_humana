"""Profession router module."""

from uuid import UUID

import fastapi
import structlog
from fastapi import Depends, Query

from app.api.schemas.profession import (
    ProfessionCreateRequest,
    ProfessionResponse,
    ProfessionUpdateRequest,
)
from app.api.services.profession import ProfessionService

logger = structlog.get_logger(__name__)

router = fastapi.APIRouter()


@router.get(
    "",
    response_model=list[ProfessionResponse],
    status_code=200,
    description="Profession endpoint to get all professions",
)
async def professions(
    include_inactive: bool = Query(default=False, description="Include inactive professions"),
    service: ProfessionService = Depends(ProfessionService),
) -> list[ProfessionResponse]:
    """
    Profession endpoint to get all professions.

    Args:
        include_inactive: Include inactive professions.
        service: Profession service dependency.

    Returns:
        list[ProfessionResponse]: List of professions.
    """
    logger.info("Getting all professions")
    return await service.get_professions(include_inactive=include_inactive)


@router.get(
    "/{profession_id}",
    response_model=ProfessionResponse,
    status_code=200,
    description="Profession endpoint to get a profession by id.",
)
async def profession_by_id(
    profession_id: UUID,
    service: ProfessionService = Depends(ProfessionService),
) -> ProfessionResponse | None:
    """
    Profession endpoint to get a profession by id.

    Args:
        profession_id: Profession id.
        service: Profession service dependency.

    Returns:
        ProfessionResponse: Profession.
    """
    logger.info("Getting profession by id")
    logger.info(f"Profession id: {profession_id}")
    return await service.get_profession_by_id(profession_id)


@router.post(
    "",
    response_model=ProfessionResponse,
    status_code=201,
    description="Profession endpoint to create a profession.",
)
async def create_profession(
    profession: ProfessionCreateRequest,
    service: ProfessionService = Depends(ProfessionService),
) -> ProfessionResponse:
    """
    Profession endpoint to create a profession.

    Args:
        profession: Profession data.
        service: Profession service dependency.

    Returns:
        ProfessionResponse: Profession.
    """
    logger.info("Creating profession")
    logger.info(f"Profession: {profession}")
    return await service.create_profession(profession)


@router.put(
    "/{profession_id}",
    response_model=ProfessionResponse,
    status_code=200,
    description="Profession endpoint to update a profession.",
)
async def update_profession(
    profession_id: UUID,
    profession: ProfessionUpdateRequest,
    service: ProfessionService = Depends(ProfessionService),
) -> ProfessionResponse:
    """
    Profession endpoint to update a profession.

    Args:
        profession_id: Profession id.
        profession: Profession data.
        service: Profession service dependency.

    Returns:
        ProfessionResponse: Profession.
    """
    logger.info("Updating profession")
    logger.info(f"Profession id: {profession_id}")
    logger.info(f"Profession: {profession}")
    return await service.update_profession(profession_id, profession)


@router.delete(
    "/{profession_id}",
    status_code=204,
    description="Profession endpoint to delete a profession.",
)
async def delete_profession(
    profession_id: UUID,
    service: ProfessionService = Depends(ProfessionService),
) -> None:
    """
    Profession endpoint to delete a profession.

    Args:
        profession_id: Profession id.
        service: Profession service dependency.

    Returns:
        None.
    """
    logger.info("Deleting profession")
    logger.info(f"Profession id: {profession_id}")
    return await service.delete_profession(profession_id)
