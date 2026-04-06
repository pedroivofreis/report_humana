"""Shift Service."""

from datetime import datetime, timedelta
from uuid import UUID

from fastapi import Depends

from app.api.models.shifts import Shift, ShiftSlotConfig
from app.api.models.user_shifts import ShiftStatus, UserShift
from app.api.repositories.shift_repository import ShiftRepository
from app.api.schemas.shifts import ShiftCreate, ShiftResponse, ShiftUpdate
from app.core.exceptions import BadRequestException


class ShiftService:
    """Shift Service."""

    def __init__(self, repository: ShiftRepository = Depends(ShiftRepository)):
        self.repository = repository

    async def create_shift(self, shift_create: ShiftCreate) -> Shift:
        """Create a new shift."""
        shift_data = shift_create.model_dump()

        if not shift_data.get("shift_weight"):
            shift_data["shift_weight"] = shift_create.duration_hours / 12.0

        if not shift_data.get("end_time"):
            start_h, start_m = map(int, shift_create.start_time.split(":"))
            start_dt = datetime.now().replace(hour=start_h, minute=start_m, second=0, microsecond=0)
            end_dt = start_dt + timedelta(hours=shift_create.duration_hours)
            shift_data["end_time"] = end_dt.strftime("%H:%M")

        shift = Shift(**shift_data)

        vacancy_count = shift.vacancy_count or 1
        for i in range(vacancy_count):
            slot_config = ShiftSlotConfig(slot_index=i, shift=shift)
            shift.slots.append(slot_config)

        await self.repository.create_shift(shift)
        await self._generate_user_shifts_for_shift(shift)

        return shift

    async def _generate_user_shifts_for_shift(self, shift: Shift) -> None:
        """Generate user shifts for a shift."""
        if not shift.days_of_week or not shift.end_date:
            raise BadRequestException("Plantão deve ter dias da semana e data final")

        current_date = shift.start_date
        end_date = shift.end_date

        start_h, start_m = map(int, shift.start_time.split(":"))
        end_h, end_m = map(int, shift.end_time.split(":"))

        slots_map = {slot.slot_index: slot for slot in shift.slots}

        while current_date <= end_date:
            system_weekday = (current_date.weekday() + 1) % 7

            if system_weekday in shift.days_of_week:
                vacancy_count = shift.vacancy_count or 1
                for i in range(vacancy_count):
                    planned_start = datetime.combine(current_date, datetime.min.time()) + timedelta(
                        hours=start_h, minutes=start_m
                    )

                    if (end_h < start_h) or (end_h == start_h and end_m < start_m):
                        planned_end_date = current_date + timedelta(days=1)
                    else:
                        planned_end_date = current_date

                    planned_end = datetime.combine(
                        planned_end_date, datetime.min.time()
                    ) + timedelta(hours=end_h, minutes=end_m)

                    slot_config = slots_map.get(i)
                    assigned_user_id = slot_config.fixed_user_id if slot_config else None
                    slot_config_id = slot_config.id if slot_config else None
                    status = ShiftStatus.PLANNED if assigned_user_id else ShiftStatus.OPEN

                    user_shift = UserShift(
                        shift_id=shift.id,
                        user_id=assigned_user_id,
                        slot_config_id=slot_config_id,
                        date=current_date,
                        competence_date=current_date.strftime("%Y-%m"),
                        planned_start=planned_start,
                        planned_end=planned_end,
                        agreed_value=shift.base_value,
                        status=status,
                        weight=shift.shift_weight,
                    )
                    await self.repository.create_user_shift(user_shift)

            current_date += timedelta(days=1)

    async def get_all_shifts(
        self,
        sector_id: UUID | None = None,
        institution_id: UUID | None = None,
        include_deleted: bool = False,
    ) -> list[ShiftResponse]:
        """Get all shifts."""
        return await self.repository.get_all_shifts(
            sector_id=sector_id,
            institution_id=institution_id,
            include_deleted=include_deleted,
        )

    async def get_shift(self, shift_id: UUID) -> Shift | None:
        """Get a shift by ID."""
        return await self.repository.get_shift(shift_id)

    async def update_shift(self, shift_id: UUID, update_data: ShiftUpdate) -> Shift | None:
        """Update a shift."""
        shift = await self.repository.get_shift(shift_id)
        if not shift:
            return None

        for key, value in update_data.model_dump(exclude={"slots"}, exclude_unset=True).items():
            setattr(shift, key, value)

        if update_data.slots is not None:

            existing_slots_map = {slot.slot_index: slot for slot in shift.slots}

            for slot_update in update_data.slots:
                if slot_update.slot_index in existing_slots_map:
                    existing_slot = existing_slots_map[slot_update.slot_index]
                    for key, value in slot_update.model_dump(exclude_unset=True).items():
                        setattr(existing_slot, key, value)
                else:
                    new_slot = ShiftSlotConfig(**slot_update.model_dump())
                    shift.slots.append(new_slot)

        return await self.repository.update_shift(
            shift, update_data.model_dump(exclude={"slots"}, exclude_unset=True)
        )
