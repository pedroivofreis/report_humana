"""Complementary data service module."""

from uuid import UUID

import structlog
from fastapi import Depends

from app.api.models.complementary_data import ComplementaryData
from app.api.repositories.complementary_data import ComplementaryDataRepository
from app.api.repositories.user import UserRepository
from app.api.schemas.complementary_data import (
    ComplementaryDataCreateRequest,
    ComplementaryDataUpdateRequest,
)
from app.core.exceptions import BadRequestException, NotFoundException

logger = structlog.getLogger(__name__)


class ComplementaryDataService:
    """Complementary data service."""

    def __init__(
        self,
        repository: ComplementaryDataRepository = Depends(ComplementaryDataRepository),
        user_repository: UserRepository = Depends(UserRepository),
    ):
        """Initialize complementary data service."""
        self.repository = repository
        self.user_repository = user_repository

    async def get_by_user_id(self, user_id: UUID) -> ComplementaryData:
        """Get complementary data by user id."""
        logger.debug(f"Get complementary data by user id: {user_id}")

        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        complementary_data = await self.repository.get_by_user_id(user_id)
        if not complementary_data:
            raise NotFoundException("Complementary data not found for this user")

        return complementary_data

    async def create(
        self, user_id: UUID, complementary_data: ComplementaryDataCreateRequest
    ) -> ComplementaryData:
        """Create complementary data."""
        logger.debug(f"Create complementary data for user id: {user_id}")

        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        existing_data = await self.repository.get_by_user_id(user_id)
        if existing_data:
            raise BadRequestException("Complementary data already exists for this user")

        if complementary_data.has_disability is True and not complementary_data.disability:
            raise BadRequestException("Disability field is required when has_disability is True")

        return await self.repository.create(user_id, complementary_data)

    async def update(
        self, user_id: UUID, complementary_data: ComplementaryDataUpdateRequest
    ) -> ComplementaryData:
        """Update complementary data."""
        logger.debug(f"Update complementary data for user id: {user_id}")

        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        if complementary_data.has_disability is True and not complementary_data.disability:
            raise BadRequestException("Disability field is required when has_disability is True")

        return await self.repository.update_or_create(user_id, complementary_data)

    async def delete(self, user_id: UUID) -> None:
        """Delete complementary data."""
        logger.debug(f"Delete complementary data for user id: {user_id}")

        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        deleted = await self.repository.delete(user_id)
        if not deleted:
            raise NotFoundException("Complementary data not found for this user")
