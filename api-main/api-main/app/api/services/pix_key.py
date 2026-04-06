"""Pix key service module."""

from uuid import UUID

import structlog
from fastapi import Depends

from app.api.repositories.pix_key import PixKeyRepository
from app.api.schemas.pix_key import PixKeyCreateRequest, PixKeyResponse, PixKeyUpdateRequest
from app.core.exceptions import NotFoundException

logger = structlog.getLogger(__name__)


class PixKeyService:
    """Pix key service."""

    def __init__(self, repository: PixKeyRepository = Depends(PixKeyRepository)):
        self.repository = repository

    async def get_pix_keys(self, include_inactive: bool = False) -> list[PixKeyResponse]:
        """Get all pix keys."""
        logger.debug("Get all pix keys")
        return await self.repository.get_pix_keys(include_inactive=include_inactive)

    async def get_pix_keys_by_user_id(
        self, user_id: UUID, include_inactive: bool = False
    ) -> list[PixKeyResponse]:
        """Get pix keys by user id."""
        logger.debug(f"Get pix keys by user id: {user_id}")
        return await self.repository.get_pix_keys_by_user_id(
            user_id, include_inactive=include_inactive
        )

    async def get_main_pix_key_by_user_id(self, user_id: UUID) -> PixKeyResponse | None:
        """Get main pix key by user id."""
        logger.debug(f"Get main pix key by user id: {user_id}")
        return await self.repository.get_main_pix_key_by_user_id(user_id)

    async def get_pix_key_by_id(self, pix_key_id: UUID) -> PixKeyResponse | None:
        """Get a pix key by id."""
        logger.debug(f"Get pix key by id: {pix_key_id}")
        pix_key = await self.repository.get_pix_key_by_id(pix_key_id)
        if not pix_key:
            raise NotFoundException("Pix key not found")

        return pix_key

    async def create_pix_key(self, pix_key: PixKeyCreateRequest) -> PixKeyResponse:
        """Create a pix key."""
        logger.debug("Create pix key service")
        return await self.repository.create_pix_key(pix_key)

    async def update_pix_key(
        self, pix_key_id: UUID, pix_key: PixKeyUpdateRequest
    ) -> PixKeyResponse:
        """Update a pix key."""
        logger.debug(f"Update pix key by id: {pix_key_id}")

        if await self.repository.get_pix_key_by_id(pix_key_id) is None:
            raise NotFoundException("Pix key not found")

        return await self.repository.update_pix_key(pix_key_id, pix_key)

    async def delete_pix_key(self, pix_key_id: UUID) -> None:
        """Delete a pix key."""
        logger.debug(f"Delete pix key by id: {pix_key_id}")

        if await self.repository.get_pix_key_by_id(pix_key_id) is None:
            raise NotFoundException("Pix key not found")

        return await self.repository.delete_pix_key(pix_key_id)
