"""Shift repository."""

from uuid import UUID

from fastapi import Depends
from sqlalchemy import select

from app.api.models.shifts import Shift
from app.api.models.user_shifts import UserShift
from app.api.repositories.base import BaseRepository
from app.api.schemas.shifts import ShiftResponse, ShiftUpdate
from app.db.session import AsyncSession, get_db_session


class ShiftRepository(BaseRepository[Shift]):
    """Shift repository."""

    def __init__(self, db: AsyncSession = Depends(get_db_session)):
        super().__init__(model=Shift, db=db)

    async def create_shift(self, shift: Shift) -> Shift:
        return await self.create(shift)

    async def get_shift(self, shift_id: UUID) -> Shift | None:
        return await self.get_by_id(shift_id)

    async def get_all_shifts(
        self,
        sector_id: UUID | None = None,
        institution_id: UUID | None = None,
        include_deleted: bool = False,
    ) -> list[ShiftResponse]:
        query = select(Shift)

        if sector_id:
            query = query.where(Shift.sector_id == sector_id)

        if institution_id:
            query = query.where(Shift.institution_id == institution_id)

        if not include_deleted:
            if hasattr(self.model, "deleted_at"):
                query = query.where(self.model.deleted_at.is_(None))

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_shift(self, shift: Shift, update_data: ShiftUpdate | dict) -> Shift | None:
        return await self.update(shift.id, update_data)

    async def delete_shift(self, id: UUID) -> None:
        """Delete a shift."""
        shift = await self.get_by_id(id)
        if not shift:
            raise ResourceNotFoundException("Turno não encontrado")
        await self.delete(id)

    async def has_active_shifts_by_type(self, shift_type_id: UUID) -> bool:
        """Check if there are any active shifts of a given type."""
        query = select(self.model).where(
            self.model.shift_type_id == shift_type_id,
            self.model.is_active == True
        ).limit(1)
        result = await self.db.execute(query)
        return result.scalars().first() is not None

    async def create_user_shift(self, user_shift: UserShift) -> None:
        self.db.add(user_shift)
        await self.db.commit()
        await self.db.refresh(user_shift)
