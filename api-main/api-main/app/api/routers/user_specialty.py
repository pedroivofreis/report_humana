"""User specialty router module."""

from uuid import UUID

import fastapi
import structlog
from fastapi import Depends, Query

from app.api.schemas.user_specialty import (
    UserSpecialtyCreateRequest,
    UserSpecialtyResponse,
    UserSpecialtyUpdateRequest,
    UserSpecialtyWithDetailsResponse,
)
from app.api.services.user_specialty import UserSpecialtyService

logger = structlog.get_logger(__name__)

router = fastapi.APIRouter()


@router.get(
    "",
    response_model=list[UserSpecialtyResponse] | list[UserSpecialtyWithDetailsResponse],
    status_code=200,
    description="User specialty endpoint to get all items",
)
async def user_specialties(
    with_details: bool = Query(default=False, description="Include specialty details"),
    service: UserSpecialtyService = Depends(UserSpecialtyService),
) -> list[UserSpecialtyResponse] | list[UserSpecialtyWithDetailsResponse]:
    """
    User specialty endpoint to get all items.

    Args:
        with_details: Include specialty details.
        service: User specialty service dependency.

    Returns:
        list[UserSpecialtyResponse] | list[UserSpecialtyWithDetailsResponse]: List of items.
    """
    logger.info("Getting all user specialties")
    return await service.get_user_specialties(with_details=with_details)


@router.get(
    "/user/{user_id}",
    response_model=list[UserSpecialtyResponse] | list[UserSpecialtyWithDetailsResponse],
    status_code=200,
    description="User specialty endpoint to get items by user id",
)
async def user_specialties_by_user_id(
    user_id: UUID,
    with_details: bool = Query(default=False, description="Include specialty details"),
    service: UserSpecialtyService = Depends(UserSpecialtyService),
) -> list[UserSpecialtyResponse] | list[UserSpecialtyWithDetailsResponse]:
    """
    User specialty endpoint to get items by user id.

    Args:
        user_id: User id.
        with_details: Include specialty details.
        service: User specialty service dependency.

    Returns:
        list[UserSpecialtyResponse] | list[UserSpecialtyWithDetailsResponse]: List of items.
    """
    logger.info("Getting user specialties by user id")
    logger.info(f"User id: {user_id}")
    return await service.get_by_user_id(user_id, with_details=with_details)


@router.get(
    "/user/{user_id}/primary",
    response_model=UserSpecialtyResponse | UserSpecialtyWithDetailsResponse | None,
    status_code=200,
    description="User specialty endpoint to get primary item by user id",
)
async def primary_user_specialty_by_user_id(
    user_id: UUID,
    with_details: bool = Query(default=False, description="Include specialty details"),
    service: UserSpecialtyService = Depends(UserSpecialtyService),
) -> UserSpecialtyResponse | UserSpecialtyWithDetailsResponse | None:
    """
    User specialty endpoint to get primary item by user id.

    Args:
        user_id: User id.
        with_details: Include specialty details.
        service: User specialty service dependency.

    Returns:
        UserSpecialtyResponse | UserSpecialtyWithDetailsResponse | None: Primary item or None.
    """
    logger.info("Getting primary user specialty by user id")
    logger.info(f"User id: {user_id}")
    return await service.get_primary_by_user_id(user_id, with_details=with_details)


@router.get(
    "/{item_id}",
    response_model=UserSpecialtyResponse | UserSpecialtyWithDetailsResponse,
    status_code=200,
    description="User specialty endpoint to get an item by id.",
)
async def user_specialty_by_id(
    item_id: UUID,
    with_details: bool = Query(default=False, description="Include specialty details"),
    service: UserSpecialtyService = Depends(UserSpecialtyService),
) -> UserSpecialtyResponse | UserSpecialtyWithDetailsResponse | None:
    """
    User specialty endpoint to get an item by id.

    Args:
        item_id: Item id.
        with_details: Include specialty details.
        service: User specialty service dependency.

    Returns:
        UserSpecialtyResponse | UserSpecialtyWithDetailsResponse: Item.
    """
    logger.info("Getting user specialty by id")
    logger.info(f"Item id: {item_id}")
    return await service.get_user_specialty_by_id(item_id, with_details=with_details)


@router.post(
    "",
    response_model=UserSpecialtyResponse,
    status_code=201,
    description="User specialty endpoint to create an item.",
)
async def create_user_specialty(
    item: UserSpecialtyCreateRequest,
    service: UserSpecialtyService = Depends(UserSpecialtyService),
) -> UserSpecialtyResponse:
    """
    User specialty endpoint to create an item.

    Args:
        item: Item data.
        service: User specialty service dependency.

    Returns:
        UserSpecialtyResponse: Item.
    """
    logger.info("Creating user specialty")
    logger.info(f"Item: {item}")
    return await service.create_user_specialty(item)


@router.put(
    "/{item_id}",
    response_model=UserSpecialtyResponse,
    status_code=200,
    description="User specialty endpoint to update an item.",
)
async def update_user_specialty(
    item_id: UUID,
    item: UserSpecialtyUpdateRequest,
    service: UserSpecialtyService = Depends(UserSpecialtyService),
) -> UserSpecialtyResponse:
    """
    User specialty endpoint to update an item.

    Args:
        item_id: Item id.
        item: Item data.
        service: User specialty service dependency.

    Returns:
        UserSpecialtyResponse: Item.
    """
    logger.info("Updating user specialty")
    logger.info(f"Item id: {item_id}")
    logger.info(f"Item: {item}")
    return await service.update_user_specialty(item_id, item)


@router.delete(
    "/{item_id}",
    status_code=204,
    description="User specialty endpoint to delete an item.",
)
async def delete_user_specialty(
    item_id: UUID,
    service: UserSpecialtyService = Depends(UserSpecialtyService),
) -> None:
    """
    User specialty endpoint to delete an item.

    Args:
        item_id: Item id.
        service: User specialty service dependency.

    Returns:
        None.
    """
    logger.info("Deleting user specialty")
    logger.info(f"Item id: {item_id}")
    return await service.delete_user_specialty(item_id)
