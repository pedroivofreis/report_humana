"""Pix key router module."""

from uuid import UUID

import fastapi
import structlog
from fastapi import Depends, Query

from app.api.schemas.pix_key import PixKeyCreateRequest, PixKeyResponse, PixKeyUpdateRequest
from app.api.services.pix_key import PixKeyService

logger = structlog.get_logger(__name__)

router = fastapi.APIRouter()


@router.get(
    "",
    response_model=list[PixKeyResponse],
    status_code=200,
    description="Pix key endpoint to get all pix keys",
)
async def pix_keys(
    include_inactive: bool = Query(default=False, description="Include inactive pix keys"),
    service: PixKeyService = Depends(PixKeyService),
) -> list[PixKeyResponse]:
    """
    Pix key endpoint to get all pix keys.

    Args:
        include_inactive: Include inactive pix keys.
        service: Pix key service dependency.

    Returns:
        list[PixKeyResponse]: List of pix keys.
    """
    logger.info("Getting all pix keys")
    return await service.get_pix_keys(include_inactive=include_inactive)


@router.get(
    "/user/{user_id}",
    response_model=list[PixKeyResponse],
    status_code=200,
    description="Pix key endpoint to get pix keys by user id",
)
async def pix_keys_by_user_id(
    user_id: UUID,
    include_inactive: bool = Query(default=False, description="Include inactive pix keys"),
    service: PixKeyService = Depends(PixKeyService),
) -> list[PixKeyResponse]:
    """
    Pix key endpoint to get pix keys by user id.

    Args:
        user_id: User id.
        include_inactive: Include inactive pix keys.
        service: Pix key service dependency.

    Returns:
        list[PixKeyResponse]: List of pix keys.
    """
    logger.info("Getting pix keys by user id")
    logger.info(f"User id: {user_id}")
    return await service.get_pix_keys_by_user_id(user_id, include_inactive=include_inactive)


@router.get(
    "/user/{user_id}/main",
    response_model=PixKeyResponse | None,
    status_code=200,
    description="Pix key endpoint to get main pix key by user id",
)
async def main_pix_key_by_user_id(
    user_id: UUID,
    service: PixKeyService = Depends(PixKeyService),
) -> PixKeyResponse | None:
    """
    Pix key endpoint to get main pix key by user id.

    Args:
        user_id: User id.
        service: Pix key service dependency.

    Returns:
        PixKeyResponse | None: Main pix key or None.
    """
    logger.info("Getting main pix key by user id")
    logger.info(f"User id: {user_id}")
    return await service.get_main_pix_key_by_user_id(user_id)


@router.get(
    "/{pix_key_id}",
    response_model=PixKeyResponse,
    status_code=200,
    description="Pix key endpoint to get a pix key by id.",
)
async def pix_key_by_id(
    pix_key_id: UUID,
    service: PixKeyService = Depends(PixKeyService),
) -> PixKeyResponse | None:
    """
    Pix key endpoint to get a pix key by id.

    Args:
        pix_key_id: Pix key id.
        service: Pix key service dependency.

    Returns:
        PixKeyResponse: Pix key.
    """
    logger.info("Getting pix key by id")
    logger.info(f"Pix key id: {pix_key_id}")
    return await service.get_pix_key_by_id(pix_key_id)


@router.post(
    "",
    response_model=PixKeyResponse,
    status_code=201,
    description="Pix key endpoint to create a pix key.",
)
async def create_pix_key(
    pix_key: PixKeyCreateRequest,
    service: PixKeyService = Depends(PixKeyService),
) -> PixKeyResponse:
    """
    Pix key endpoint to create a pix key.

    Args:
        pix_key: Pix key data.
        service: Pix key service dependency.

    Returns:
        PixKeyResponse: Pix key.
    """
    logger.info("Creating pix key")
    logger.info(f"Pix key: {pix_key}")
    return await service.create_pix_key(pix_key)


@router.put(
    "/{pix_key_id}",
    response_model=PixKeyResponse,
    status_code=200,
    description="Pix key endpoint to update a pix key.",
)
async def update_pix_key(
    pix_key_id: UUID,
    pix_key: PixKeyUpdateRequest,
    service: PixKeyService = Depends(PixKeyService),
) -> PixKeyResponse:
    """
    Pix key endpoint to update a pix key.

    Args:
        pix_key_id: Pix key id.
        pix_key: Pix key data.
        service: Pix key service dependency.

    Returns:
        PixKeyResponse: Pix key.
    """
    logger.info("Updating pix key")
    logger.info(f"Pix key id: {pix_key_id}")
    logger.info(f"Pix key: {pix_key}")
    return await service.update_pix_key(pix_key_id, pix_key)


@router.delete(
    "/{pix_key_id}",
    status_code=204,
    description="Pix key endpoint to delete a pix key.",
)
async def delete_pix_key(
    pix_key_id: UUID,
    service: PixKeyService = Depends(PixKeyService),
) -> None:
    """
    Pix key endpoint to delete a pix key.

    Args:
        pix_key_id: Pix key id.
        service: Pix key service dependency.

    Returns:
        None.
    """
    logger.info("Deleting pix key")
    logger.info(f"Pix key id: {pix_key_id}")
    return await service.delete_pix_key(pix_key_id)
