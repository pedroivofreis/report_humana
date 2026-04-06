"""User Shift repository."""

from datetime import date, datetime
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.models.shifts import Shift
from app.api.models.user import User
from app.api.models.user_shifts import ShiftExchange, ShiftStatus, UserShift
from app.api.repositories.base import BaseRepository
from app.api.schemas.user_shifts import UserShiftDetailResponse, UserShiftResponse
from app.db.session import get_db_session


class UserShiftRepository(BaseRepository[UserShift]):
    """User Shift repository."""

    def __init__(self, db: AsyncSession = Depends(get_db_session)):
        super().__init__(model=UserShift, db=db)

    async def create_user_shift(self, user_shift: UserShift) -> UserShiftResponse:
        """Create a new user shift."""
        result = await self.create(user_shift)

        query = (
            select(UserShift)
            .options(
                selectinload(UserShift.shift),
                selectinload(UserShift.slot_config),
                selectinload(UserShift.user),
                selectinload(UserShift.assistance_user),
            )
            .where(UserShift.id == result.id)
        )
        refresh_result = await self.db.execute(query)
        refreshed_shift = refresh_result.scalar_one()

        return UserShiftResponse.model_validate(refreshed_shift)

    async def get_user_shift(self, shift_id: UUID) -> UserShiftResponse | None:
        """Get a user shift by id."""
        result = await self.get_by_id(shift_id)
        return UserShiftResponse.model_validate(result)

    async def get_all_user_shifts(self, include_deleted: bool = False) -> list[UserShiftResponse]:
        """Get all user shifts."""
        result = await self.get_all(include_deleted=include_deleted)
        return [UserShiftResponse.model_validate(shift) for shift in result]

    async def update_user_shift(self, user_shift: UserShift) -> UserShift:
        """Update a user shift."""
        await self.db.flush()

        query = (
            select(UserShift)
            .options(
                selectinload(UserShift.user),
                selectinload(UserShift.assistance_user),
            )
            .where(UserShift.id == user_shift.id)
        )
        result = await self.db.execute(query)
        refreshed_shift = result.scalar_one()

        return refreshed_shift

    async def get_shifts_by_user_and_date_range(
        self, user_id: UUID, start_date: date, end_date: date
    ) -> list[UserShift]:
        """Get shifts for a user within a date range."""
        query = (
            select(UserShift)
            .where(UserShift.user_id == user_id)
            .where(UserShift.date >= start_date)
            .where(UserShift.date <= end_date)
            .options(selectinload(UserShift.slot_config))
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_planned_shift_in_window(
        self, user_id: UUID, start_window: datetime, end_window: datetime
    ) -> UserShift | None:
        """Get planned shift for user within time window."""
        query = select(UserShift).where(
            UserShift.user_id == user_id,
            UserShift.status == ShiftStatus.PLANNED,
            UserShift.planned_start >= start_window,
            UserShift.planned_start <= end_window,
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_in_progress_shift(self, user_id: UUID) -> UserShift | None:
        """Get in-progress shift for user."""
        query = select(UserShift).where(
            UserShift.user_id == user_id,
            UserShift.status == ShiftStatus.IN_PROGRESS,
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_shifts_by_filter(
        self,
        institution_id: UUID,
        year_month: str,
        user_id: UUID | None = None,
        sector_id: UUID | None = None,
    ) -> list[UserShift]:
        query = (
            select(UserShift)
            .join(Shift, UserShift.shift_id == Shift.id)
            .options(
                selectinload(UserShift.shift).selectinload(Shift.sector),
                selectinload(UserShift.user),
                selectinload(UserShift.assistance_user),
            )
            .where(
                Shift.institution_id == institution_id,
                UserShift.competence_date == year_month,
                UserShift.status != ShiftStatus.CANCELED,
            )
        )

        if user_id:
            query = query.where(UserShift.user_id == user_id)

        if sector_id:
            query = query.where(Shift.sector_id == sector_id)

        query = query.order_by(UserShift.date, UserShift.planned_start)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_shift_with_details(self, shift_id: UUID) -> UserShiftDetailResponse | None:
        """Get user shift with details."""
        from sqlalchemy.orm import joinedload

        from app.api.schemas.user_shifts import UserShiftDetailResponse

        query = (
            select(UserShift)
            .options(
                joinedload(UserShift.shift).joinedload(Shift.shift_type),
                joinedload(UserShift.shift).joinedload(Shift.slots),
                joinedload(UserShift.slot_config),
                joinedload(UserShift.exchanges).joinedload(ShiftExchange.target_user),
                joinedload(UserShift.exchanges).joinedload(ShiftExchange.old_person),
                joinedload(UserShift.user),
                joinedload(UserShift.assistance_user),
            )
            .where(UserShift.id == shift_id)
        )
        result = await self.db.execute(query)
        shift = result.unique().scalar_one_or_none()
        if shift:
            response = UserShiftDetailResponse.model_validate(shift)
            shift.exchanges.sort(key=lambda x: x.requested_at or datetime.min)

            from app.api.schemas.user_shifts import ShiftExchangeResponse

            response.shift_exchanges = [
                ShiftExchangeResponse.model_validate(e) for e in shift.exchanges
            ]
            return response
        return None

    async def get_shift_with_institution_and_sector(self, shift_id: UUID) -> UserShift:
        """Get user shift with institution and sector."""
        from sqlalchemy.orm import joinedload

        query = (
            select(UserShift)
            .options(
                joinedload(UserShift.shift).joinedload(Shift.institution),
                joinedload(UserShift.shift).joinedload(Shift.sector),
            )
            .where(UserShift.id == shift_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_candidate_shifts_for_bulk(
        self,
        start_date: date,
        end_date: date,
        sector_id: UUID,
        shift_id: UUID | None = None,
        shift_type_id: UUID | None = None,
    ) -> list[UserShift]:
        """Fetch available UserShifts for bulk assignment."""
        query = (
            select(UserShift)
            .join(Shift, UserShift.shift_id == Shift.id)
            .where(
                UserShift.date >= start_date,
                UserShift.date <= end_date,
                UserShift.user_id.is_(None),
                UserShift.status.in_([ShiftStatus.OPEN, ShiftStatus.PLANNED]),
                Shift.sector_id == sector_id,
            )
        )

        if shift_id:
            query = query.where(UserShift.shift_id == shift_id)

        if shift_type_id:
            query = query.where(Shift.shift_type_id == shift_type_id)

        query = query.order_by(UserShift.planned_start)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_shifts_grouped_by_sector(
        self,
        competence_date: str,
        user_id: UUID | None = None,
        sector_ids: list[UUID] | None = None,
        status: ShiftStatus | None = None,
    ) -> list[UserShift]:
        """Get all shifts for a competence date grouped by sector, including those without timesheet."""

        query = (
            select(UserShift)
            .join(Shift, UserShift.shift_id == Shift.id)
            .options(
                selectinload(UserShift.shift).selectinload(Shift.sector),
                selectinload(UserShift.shift).selectinload(Shift.institution),
                selectinload(UserShift.user).selectinload(User.professional_crms),
            )
            .where(UserShift.competence_date == competence_date)
        )

        if user_id is not None:
            query = query.where(UserShift.user_id == user_id)

        if sector_ids is not None and len(sector_ids) > 0:
            query = query.where(Shift.sector_id.in_(sector_ids))

        if status is not None:
            query = query.where(UserShift.status == status)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def has_active_shifts_for_sector(self, sector_id: UUID) -> bool:
        """Check if a sector has active user shifts."""
        query = (
            select(UserShift.id)
            .join(Shift, UserShift.shift_id == Shift.id)
            .where(
                Shift.sector_id == sector_id,
                UserShift.status.in_(
                    [
                        ShiftStatus.OPEN,
                        ShiftStatus.PLANNED,
                        ShiftStatus.CONFIRMED,
                        ShiftStatus.IN_PROGRESS,
                    ]
                ),
            )
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
