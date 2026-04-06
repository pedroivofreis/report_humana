"""User Absence service."""

from uuid import UUID

from fastapi import Depends

from app.api.models.user_absence import UserAbsence
from app.api.repositories.user_absence_repository import UserAbsenceRepository
from app.api.repositories.user_shift_repository import UserShiftRepository
from app.api.schemas.user_absence import UserAbsenceCreate


class UserAbsenceService:
    def __init__(
        self,
        repository: UserAbsenceRepository = Depends(UserAbsenceRepository),
        user_shift_repository: UserShiftRepository = Depends(UserShiftRepository),
    ):
        self.repository = repository
        self.user_shift_repository = user_shift_repository

    async def create_absence(self, absence_in: UserAbsenceCreate) -> UserAbsence:
        absence = UserAbsence(**absence_in.model_dump())
        created_absence = await self.repository.create_with_user(absence)

        start_date = created_absence.start_date
        end_date = created_absence.end_date

        shifts = await self.user_shift_repository.get_shifts_by_user_and_date_range(
            user_id=created_absence.user_id, start_date=start_date, end_date=end_date
        )

        for shift in shifts:
            if shift.slot_config and shift.slot_config.is_fixed:
                if shift.slot_config.fixed_user_id == created_absence.user_id:
                    shift.needs_assistance = True
                    shift.assistance_reason = created_absence.type.value
                    self.repository.db.add(shift)

        await self.repository.db.commit()
        return created_absence

    async def get_user_absences(self, user_id: UUID) -> list[UserAbsence]:
        return await self.repository.get_by_user(user_id)

    async def get_absences_by_sector(self, sector_id: UUID) -> list[UserAbsence]:
        return await self.repository.get_by_sector(sector_id)
