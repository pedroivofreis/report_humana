"""Shift Type repository."""

from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.models.shift_types import ShiftType
from app.api.repositories.base import BaseRepository
from app.db.session import get_db_session


class ShiftTypeRepository(BaseRepository[ShiftType]):
    """Shift Type repository."""

    def __init__(self, db: AsyncSession = Depends(get_db_session)):
        super().__init__(model=ShiftType, db=db)

    async def get_types_by_institution_id(
        self, institution_id: UUID, include_deleted: bool = False
    ) -> list[ShiftType]:
        """Get shift types by institution ID."""
        query = select(self.model).where(self.model.institution_id == institution_id)
        if not include_deleted and hasattr(self.model, "active"):
            query = query.where(self.model.active == True)  # noqa: E712

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_all(self, include_deleted: bool = False) -> list[ShiftType]:
        """Get all shift types."""
        query = select(self.model)
        if not include_deleted and hasattr(self.model, "active"):
            query = query.where(self.model.active == True)  # noqa: E712

        result = await self.db.execute(query)
        return list(result.scalars().all())
