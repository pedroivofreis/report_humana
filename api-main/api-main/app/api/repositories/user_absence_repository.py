"""User Absence repository."""

from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import cast

from app.api.models.user_absence import UserAbsence
from app.api.repositories.base import BaseRepository
from app.db.session import get_db_session


class UserAbsenceRepository(BaseRepository[UserAbsence]):
    def __init__(self, db: AsyncSession = Depends(get_db_session)):
        super().__init__(model=UserAbsence, db=db)

    async def create_with_user(self, absence: UserAbsence) -> UserAbsence:
        """Create an absence and return it with the user relationship eagerly loaded."""
        self.db.add(absence)
        await self.db.flush()
        stmt = (
            select(UserAbsence)
            .where(UserAbsence.id == absence.id)
            .options(selectinload(UserAbsence.user))
        )
        result = await self.db.execute(stmt)
        return cast(UserAbsence, result.scalar_one())

    async def get_by_user(self, user_id: UUID) -> list[UserAbsence]:
        stmt = (
            select(UserAbsence)
            .where(UserAbsence.user_id == user_id)
            .options(selectinload(UserAbsence.user))
        )
        result = await self.db.execute(stmt)
        return cast(list[UserAbsence], result.scalars().all())

    async def get_by_sector(self, sector_id: UUID) -> list[UserAbsence]:
        stmt = (
            select(UserAbsence)
            .where(UserAbsence.sector_id == sector_id)
            .options(selectinload(UserAbsence.user))
        )
        result = await self.db.execute(stmt)
        return cast(list[UserAbsence], result.scalars().all())
