"""User Timesheet repository module."""

from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, select
from sqlalchemy.orm import contains_eager, joinedload, selectinload

from app.api.models.attachment import Attachment
from app.api.models.user import User
from app.api.models.user_timesheets import TimesheetStatus, UserTimesheet
from app.api.repositories.base import BaseRepository
from app.api.schemas.user_timesheets import UserTimesheetResponse
from app.db.session import AsyncSession, get_db_session


class UserTimesheetRepository(BaseRepository[UserTimesheet]):
    """User Timesheet repository."""

    def __init__(self, db: AsyncSession = Depends(get_db_session)):
        super().__init__(model=UserTimesheet, db=db)

    async def create_user_timesheet(self, user_timesheet: UserTimesheet) -> UserTimesheet:
        """Create a new user timesheet."""
        return await self.create(user_timesheet)

    async def get_user_timesheet(self, user_timesheet_id: UUID) -> UserTimesheet | None:
        """Get a user timesheet by id."""

        query = (
            select(UserTimesheet)
            .options(selectinload(UserTimesheet.shifts))
            .where(UserTimesheet.id == user_timesheet_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all_user_timesheets(
        self, include_deleted: bool = False
    ) -> list[UserTimesheetResponse]:
        """Get all user timesheets."""
        result = await self.get_all(include_deleted=include_deleted)
        return [UserTimesheetResponse.model_validate(timesheet) for timesheet in result]

    async def update_user_timesheet(
        self, user_timesheet_id: UUID, user_timesheet: UserTimesheet | dict
    ) -> UserTimesheet | None:
        """Update a user timesheet."""
        if isinstance(user_timesheet, UserTimesheet):
            update_data = {
                "total_hours_realized": user_timesheet.total_hours_realized,
                "total_value_payable": user_timesheet.total_value_payable,
                "total_value_planned": user_timesheet.total_value_planned,
            }
            return await self.update(user_timesheet_id, update_data)

        return await self.update(user_timesheet_id, user_timesheet)

    async def get_by_user_and_competence(
        self, user_id: UUID, competence: str
    ) -> UserTimesheet | None:
        """Get user timesheet by user and competence."""
        query = select(UserTimesheet).where(
            UserTimesheet.user_id == user_id,
            UserTimesheet.competence_date == competence,
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def delete_user_timesheet(self, user_timesheet_id: UUID) -> None:
        """Delete a user timesheet."""
        await self.delete(user_timesheet_id)

    async def get_timesheets_with_details(
        self,
        competence_date: str,
        user_id: UUID | None = None,
        sector_ids: list[UUID] | None = None,
        status: TimesheetStatus | None = None,
    ) -> list[UserTimesheet]:
        """
        Get timesheets with all related data (user, sector, institution, shifts).

        Args:
            competence_date: Filter by competence date (required, format: YYYY-MM)
            user_id: Filter by user ID (optional)
            sector_ids: Filter by sector IDs - accepts one or more (optional)
            status: Filter by status (optional)

        Returns:
            List of UserTimesheet objects with eagerly loaded relationships
        """
        query = (
            select(UserTimesheet)
            .options(
                selectinload(UserTimesheet.shifts),
                joinedload(UserTimesheet.user).selectinload(User.professional_crms),
                joinedload(UserTimesheet.sector),
                joinedload(UserTimesheet.institution),
            )
            .where(UserTimesheet.competence_date == competence_date)
        )

        # Apply optional filters
        if user_id is not None:
            query = query.where(UserTimesheet.user_id == user_id)
        if sector_ids is not None and len(sector_ids) > 0:
            query = query.where(UserTimesheet.sector_id.in_(sector_ids))
        if status is not None:
            query = query.where(UserTimesheet.status == status)

        result = await self.db.execute(query)
        return list(result.unique().scalars().all())

    async def get_user_timesheet_with_details(
        self, user_timesheet_id: UUID
    ) -> UserTimesheet | None:
        """
        Get a single user timesheet with all related data.
        """
        query = (
            select(UserTimesheet)
            .outerjoin(User, UserTimesheet.user)
            .options(
                selectinload(UserTimesheet.shifts),
                contains_eager(UserTimesheet.user)
                .selectinload(User.professional_crms),
                joinedload(UserTimesheet.sector),
                joinedload(UserTimesheet.institution),
            )
            .where(UserTimesheet.id == user_timesheet_id)
            .execution_options(populate_existing=True)
        )
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()
