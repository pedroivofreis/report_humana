"""Complementary data repository module."""

import logging
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select

from app.api.models.complementary_data import ComplementaryData
from app.api.schemas.complementary_data import (
    ComplementaryDataCreateRequest,
    ComplementaryDataUpdateRequest,
)
from app.core.exceptions import NotFoundException
from app.db.session import AsyncSession, get_db_session

logger = logging.getLogger(__name__)


class ComplementaryDataRepository:
    """Complementary data repository."""

    def __init__(self, db: AsyncSession = Depends(get_db_session)):
        """Initialize complementary data repository."""
        logger.info("Initializing ComplementaryDataRepository")
        self.db = db

    async def get_by_user_id(self, user_id: UUID) -> ComplementaryData | None:
        """Get complementary data by user id."""
        logger.info(f"Getting complementary data for user_id: {user_id}")
        result = await self.db.execute(
            select(ComplementaryData).filter(ComplementaryData.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self, user_id: UUID, complementary_data: ComplementaryDataCreateRequest
    ) -> ComplementaryData:
        """Create complementary data."""
        logger.info(f"Creating complementary data for user_id: {user_id}")
        db_complementary_data = ComplementaryData(
            user_id=user_id,
            **complementary_data.model_dump(exclude_unset=True),
        )
        self.db.add(db_complementary_data)
        await self.db.commit()
        await self.db.refresh(db_complementary_data)
        return db_complementary_data

    async def update_or_create(
        self,
        user_id: UUID,
        complementary_data: ComplementaryDataCreateRequest | ComplementaryDataUpdateRequest,
    ) -> ComplementaryData:
        """Update or create complementary data."""
        logger.info(f"Updating complementary data for user_id: {user_id}")
        db_complementary_data = await self.get_by_user_id(user_id)
        if not db_complementary_data:
            if isinstance(complementary_data, ComplementaryDataUpdateRequest):
                complementary_data = ComplementaryDataCreateRequest(
                    **complementary_data.model_dump(exclude_unset=True)
                )
            return await self.create(user_id, complementary_data)

        if isinstance(complementary_data, ComplementaryDataCreateRequest):
            complementary_data = ComplementaryDataUpdateRequest(
                **complementary_data.model_dump(exclude_unset=True)
            )
        updated_data = await self.update(user_id, complementary_data)
        if not updated_data:
            raise NotFoundException("Complementary data not found for this user")
        return updated_data

    async def update(
        self, user_id: UUID, complementary_data: ComplementaryDataUpdateRequest
    ) -> ComplementaryData | None:
        """Update complementary data."""
        logger.info(f"Updating complementary data for user_id: {user_id}")
        db_complementary_data = await self.get_by_user_id(user_id)
        if not db_complementary_data:
            return None

        update_data = complementary_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_complementary_data, field, value)

        await self.db.commit()
        await self.db.refresh(db_complementary_data)
        return db_complementary_data

    async def delete(self, user_id: UUID) -> bool:
        """Delete complementary data."""
        logger.info(f"Deleting complementary data for user_id: {user_id}")
        db_complementary_data = await self.get_by_user_id(user_id)
        if not db_complementary_data:
            return False

        await self.db.delete(db_complementary_data)
        await self.db.commit()
        return True
