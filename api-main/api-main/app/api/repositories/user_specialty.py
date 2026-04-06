"""User specialty repository."""

from uuid import UUID

import structlog
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.models.user_specialty import UserSpecialty
from app.api.schemas.user_specialty import (
    UserSpecialtyCreateRequest,
    UserSpecialtyResponse,
    UserSpecialtyUpdateRequest,
    UserSpecialtyWithDetailsResponse,
)
from app.core.exceptions import NotFoundException
from app.db.session import AsyncSession, get_db_session

logger = structlog.get_logger(__name__)


class UserSpecialtyRepository:
    """User specialty repository."""

    def __init__(self, db: AsyncSession = Depends(get_db_session)):
        self.db = db

    async def get_user_specialties(
        self, with_details: bool = False
    ) -> list[UserSpecialtyResponse] | list[UserSpecialtyWithDetailsResponse]:
        """Get all user specialties."""
        logger.debug("get_user_specialties called")
        query = select(UserSpecialty)

        if with_details:
            query = query.options(
                selectinload(UserSpecialty.specialty),
            )

        result = await self.db.execute(query)
        items = result.scalars().all()
        logger.debug(f"Retrieved {len(items)} user specialties")

        if with_details:
            return [UserSpecialtyWithDetailsResponse.model_validate(item) for item in items]

        return [UserSpecialtyResponse.model_validate(item) for item in items]

    async def get_user_specialty_by_id(
        self, item_id: UUID, with_details: bool = False
    ) -> UserSpecialtyResponse | UserSpecialtyWithDetailsResponse | None:
        """Get a user specialty by id."""
        logger.debug(f"get_user_specialty_by_id called for item_id={item_id}")

        query = select(UserSpecialty).where(UserSpecialty.id == item_id)

        if with_details:
            query = query.options(
                selectinload(UserSpecialty.specialty),
            )

        result = await self.db.execute(query)
        item = result.scalar_one_or_none()
        logger.debug(f"User specialty found: {item is not None}")

        if not item:
            raise NotFoundException("User specialty not found")

        if with_details:
            return UserSpecialtyWithDetailsResponse.model_validate(item)

        return UserSpecialtyResponse.model_validate(item)

    async def get_by_user_id(
        self, user_id: UUID, with_details: bool = False
    ) -> list[UserSpecialtyResponse] | list[UserSpecialtyWithDetailsResponse]:
        """Get user specialties by user id."""
        logger.debug(f"get_by_user_id called for user_id={user_id}")

        query = select(UserSpecialty).where(UserSpecialty.user_id == user_id)

        if with_details:
            query = query.options(
                selectinload(UserSpecialty.specialty),
            )

        result = await self.db.execute(query)
        items = result.scalars().all()
        logger.debug(f"Found {len(items)} user specialties")

        if with_details:
            return [UserSpecialtyWithDetailsResponse.model_validate(item) for item in items]

        return [UserSpecialtyResponse.model_validate(item) for item in items]

    async def get_primary_by_user_id(
        self, user_id: UUID, with_details: bool = False
    ) -> UserSpecialtyResponse | UserSpecialtyWithDetailsResponse | None:
        """Get primary user specialty by user id."""
        logger.debug(f"get_primary_by_user_id called for user_id={user_id}")

        query = select(UserSpecialty).where(
            UserSpecialty.user_id == user_id, UserSpecialty.is_primary
        )

        if with_details:
            query = query.options(
                selectinload(UserSpecialty.specialty),
            )

        result = await self.db.execute(query)
        item = result.scalar_one_or_none()
        logger.debug(f"Primary user specialty found: {item is not None}")

        if not item:
            return None

        if with_details:
            return UserSpecialtyWithDetailsResponse.model_validate(item)

        return UserSpecialtyResponse.model_validate(item)

    async def create_user_specialty(
        self, item: UserSpecialtyCreateRequest
    ) -> UserSpecialtyResponse:
        """Create a user specialty."""
        logger.debug("create_user_specialty called")

        if item.is_primary:
            await self._unset_primary_items(item.user_id)

        item_data = item.model_dump()
        new_item = UserSpecialty(**item_data)

        self.db.add(new_item)
        await self.db.commit()
        await self.db.refresh(new_item)

        return UserSpecialtyResponse.model_validate(new_item)

    async def update_user_specialty(
        self, item_id: UUID, item_data: UserSpecialtyUpdateRequest
    ) -> UserSpecialtyResponse:
        """Update a user specialty."""
        logger.debug(f"update_user_specialty called for item_id={item_id}")

        result = await self.db.execute(select(UserSpecialty).where(UserSpecialty.id == item_id))
        item = result.scalar_one_or_none()

        if not item:
            raise NotFoundException("User specialty not found")

        if item_data.is_primary is True:
            await self._unset_primary_items(item.user_id, exclude_id=item_id)

        for key, value in item_data.model_dump(exclude_unset=True).items():
            setattr(item, key, value)

        await self.db.commit()
        await self.db.refresh(item)

        return UserSpecialtyResponse.model_validate(item)

    async def delete_user_specialty(self, item_id: UUID) -> None:
        """Delete a user specialty."""
        logger.debug(f"delete_user_specialty called for item_id={item_id}")
        result = await self.db.execute(select(UserSpecialty).where(UserSpecialty.id == item_id))
        item = result.scalar_one_or_none()

        if not item:
            raise NotFoundException("User specialty not found")

        await self.db.delete(item)
        await self.db.commit()

    async def _unset_primary_items(self, user_id: UUID, exclude_id: UUID | None = None) -> None:
        """Unset all primary items for a user."""
        logger.debug(f"_unset_primary_items called for user_id={user_id}")
        query = select(UserSpecialty).where(
            UserSpecialty.user_id == user_id, UserSpecialty.is_primary
        )

        if exclude_id:
            query = query.where(UserSpecialty.id != exclude_id)

        result = await self.db.execute(query)
        items = result.scalars().all()

        for item in items:
            item.is_primary = False

        await self.db.commit()
