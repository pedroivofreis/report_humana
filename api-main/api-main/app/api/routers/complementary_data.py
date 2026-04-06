"""Complementary data router module."""

from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, status

from app.api.schemas.complementary_data import (
    ComplementaryDataCreateRequest,
    ComplementaryDataResponse,
    ComplementaryDataUpdateRequest,
)
from app.api.services.complementary_data import ComplementaryDataService

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get(
    "",
    response_model=ComplementaryDataResponse,
    status_code=status.HTTP_200_OK,
    description="Complementary data endpoint to get data by user id.",
)
async def get_complementary_data(
    user_id: UUID,
    service: ComplementaryDataService = Depends(ComplementaryDataService),
) -> ComplementaryDataResponse:
    """
    Get complementary data by user id.

    Args:
        user_id: User id.
        service: Complementary data service dependency.

    Returns:
        ComplementaryDataResponse: Complementary data.
    """
    logger.info("Getting complementary data by user id")
    logger.info(f"User id: {user_id}")
    complementary_data = await service.get_by_user_id(user_id)
    return ComplementaryDataResponse.model_validate(complementary_data)


@router.post(
    "",
    response_model=ComplementaryDataResponse,
    status_code=status.HTTP_201_CREATED,
    description="Complementary data endpoint to create data for a user.",
)
async def create_complementary_data(
    user_id: UUID,
    complementary_data: ComplementaryDataCreateRequest,
    service: ComplementaryDataService = Depends(ComplementaryDataService),
) -> ComplementaryDataResponse:
    """
    Create complementary data for a user.

    Args:
        user_id: User id.
        complementary_data: Complementary data.
        service: Complementary data service dependency.

    Returns:
        ComplementaryDataResponse: Complementary data.
    """
    logger.info("Creating complementary data")
    logger.info(f"User id: {user_id}")
    created_data = await service.create(user_id, complementary_data)
    return ComplementaryDataResponse.model_validate(created_data)


@router.put(
    "",
    response_model=ComplementaryDataResponse,
    status_code=status.HTTP_200_OK,
    description="Complementary data endpoint to update data for a user.",
)
async def update_complementary_data(
    user_id: UUID,
    complementary_data: ComplementaryDataUpdateRequest,
    service: ComplementaryDataService = Depends(ComplementaryDataService),
) -> ComplementaryDataResponse:
    """
    Update complementary data for a user.

    Args:
        user_id: User id.
        complementary_data: Complementary data.
        service: Complementary data service dependency.

    Returns:
        ComplementaryDataResponse: Complementary data.
    """
    logger.info("Updating complementary data")
    logger.info(f"User id: {user_id}")
    updated_data = await service.update(user_id, complementary_data)
    return ComplementaryDataResponse.model_validate(updated_data)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Complementary data endpoint to delete data for a user.",
)
async def delete_complementary_data(
    user_id: UUID,
    service: ComplementaryDataService = Depends(ComplementaryDataService),
) -> None:
    """
    Delete complementary data for a user.

    Args:
        user_id: User id.
        service: Complementary data service dependency.

    Returns:
        None.
    """
    logger.info("Deleting complementary data")
    logger.info(f"User id: {user_id}")
    await service.delete(user_id)
