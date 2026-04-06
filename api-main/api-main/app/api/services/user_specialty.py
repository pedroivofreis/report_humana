"""User specialty service module."""

from uuid import UUID

import structlog
from fastapi import Depends

from app.api.repositories.user_specialty import UserSpecialtyRepository
from app.api.schemas.user_specialty import (
    UserSpecialtyCreateRequest,
    UserSpecialtyResponse,
    UserSpecialtyUpdateRequest,
    UserSpecialtyWithDetailsResponse,
)
from app.core.exceptions import NotFoundException

logger = structlog.getLogger(__name__)


class UserSpecialtyService:
    """User specialty service."""

    def __init__(
        self,
        repository: UserSpecialtyRepository = Depends(UserSpecialtyRepository),
    ):
        self.repository = repository

    async def get_user_specialties(
        self, with_details: bool = False
    ) -> list[UserSpecialtyResponse] | list[UserSpecialtyWithDetailsResponse]:
        """Get all user specialties."""
        logger.debug("Get all user specialties")
        return await self.repository.get_user_specialties(with_details=with_details)

    async def get_by_user_id(
        self, user_id: UUID, with_details: bool = False
    ) -> list[UserSpecialtyResponse] | list[UserSpecialtyWithDetailsResponse]:
        """Get user specialties by user id."""
        logger.debug(f"Get user specialties by user id: {user_id}")
        return await self.repository.get_by_user_id(user_id, with_details=with_details)

    async def get_primary_by_user_id(
        self, user_id: UUID, with_details: bool = False
    ) -> UserSpecialtyResponse | UserSpecialtyWithDetailsResponse | None:
        """Get primary user specialty by user id."""
        logger.debug(f"Get primary user specialty by user id: {user_id}")
        return await self.repository.get_primary_by_user_id(user_id, with_details=with_details)

    async def get_user_specialty_by_id(
        self, item_id: UUID, with_details: bool = False
    ) -> UserSpecialtyResponse | UserSpecialtyWithDetailsResponse | None:
        """Get a user specialty by id."""
        logger.debug(f"Get user specialty by id: {item_id}")
        item = await self.repository.get_user_specialty_by_id(item_id, with_details=with_details)
        if not item:
            raise NotFoundException("User specialty not found")

        return item

    async def create_user_specialty(
        self, item: UserSpecialtyCreateRequest
    ) -> UserSpecialtyResponse:
        """Create a user specialty."""
        logger.debug("Create user specialty service")
        return await self.repository.create_user_specialty(item)

    async def update_user_specialty(
        self, item_id: UUID, item: UserSpecialtyUpdateRequest
    ) -> UserSpecialtyResponse:
        """Update a user specialty."""
        logger.debug(f"Update user specialty by id: {item_id}")

        if await self.repository.get_user_specialty_by_id(item_id) is None:
            raise NotFoundException("User specialty not found")

        return await self.repository.update_user_specialty(item_id, item)

    async def delete_user_specialty(self, item_id: UUID) -> None:
        """Delete a user specialty."""
        logger.debug(f"Delete user specialty by id: {item_id}")

        if await self.repository.get_user_specialty_by_id(item_id) is None:
            raise NotFoundException("User specialty not found")

        return await self.repository.delete_user_specialty(item_id)
