"""User Shift service module."""

from datetime import date as dt_date
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.models.user_shifts import (
    ShiftExchange,
    ShiftExchangeStatusEnum,
    ShiftStatus,
    UserShift,
)
from app.api.repositories.shift_repository import ShiftRepository
from app.api.repositories.user_shift_repository import UserShiftRepository
from app.api.schemas.user_shifts import (
    AssignmentStrategy,
    BulkAssignRequest,
    SectorSimpleResponse,
    ShiftExchangeCreate,
    ShiftExchangeResponse,
    UserShiftDetailResponse,
    UserShiftResponse,
    UserShiftsBySectorResponse,
    UserShiftUpdate,
)
from app.api.services.user_timesheet_service import UserTimesheetService
from app.core.exceptions import BadRequestException, NotFoundException


class UserShiftService:
    """
    Implementa Módulo 5: Controle de Aprovações, Ponto e Horas (Execução de Plantão).
    """

    TOLERANCE_MINUTES = 30

    def __init__(
        self,
        repository: UserShiftRepository = Depends(UserShiftRepository),
        shift_repository: ShiftRepository = Depends(ShiftRepository),
        user_timesheet_service: UserTimesheetService = Depends(UserTimesheetService),
    ):
        self.repository = repository
        self.shift_repository = shift_repository
        self.user_timesheet_service = user_timesheet_service

    async def create_planned_shift(self, shift: UserShift) -> UserShiftResponse:
        """
        Cria um plantão planejado e atribui ao grupo de folha de ponto se houver usuário.
        """
        if not shift.competence_date:
            shift.competence_date = shift.date.strftime("%Y-%m")

        if not shift.planned_start or not shift.planned_end:
            if not shift.shift_id:
                raise NotFoundException("Shift ID é obrigatório para calcular horários.")
            base_shift = await self.shift_repository.get_shift(shift.shift_id)
            if not base_shift:
                raise NotFoundException("Shift base não encontrado para calcular horários.")

            if not shift.planned_start:
                start_h, start_m = map(int, base_shift.start_time.split(":"))
                shift.planned_start = datetime.combine(shift.date, datetime.min.time()) + timedelta(
                    hours=start_h, minutes=start_m
                )

            if not shift.planned_end:
                shift.planned_end = shift.planned_start + timedelta(hours=base_shift.duration_hours)

        if shift.user_id:
            shift.status = ShiftStatus.PLANNED
            await self._ensure_timesheet_link(shift, persist=False)

        created_shift = await self.repository.create_user_shift(shift)

        if created_shift.user_timesheet_id:
            await self.user_timesheet_service.update_has_shifts_stats(
                created_shift.user_timesheet_id
            )

        return created_shift

    async def _ensure_timesheet_link(self, shift: UserShift, persist: bool = True) -> None:
        """
        Internal helper to link shift to a user timesheet.
        """
        if not shift.user_id:
            shift.user_timesheet_id = None
            if persist:
                await self.repository.update_user_shift(shift)
            return

        user_id = shift.assistance_user_id or shift.user_id
        ref_date = shift.date or shift.planned_start.date()

        base_shift = await self.shift_repository.get_shift(shift.shift_id)
        institution_id = base_shift.institution_id
        sector_id = base_shift.sector_id

        user_timesheet = await self.user_timesheet_service.find_or_create_open_user_timesheet(
            user_id, institution_id, sector_id, ref_date
        )
        shift.user_timesheet_id = user_timesheet.id

        if persist:
            await self.repository.update_user_shift(shift)

    async def perform_checkin(self, user_id: UUID, lat: float, long: float) -> dict:
        """
        Valida janela de tempo e geolocalização antes de abrir o plantão.
        """
        now = datetime.now()

        start_window = now - timedelta(minutes=self.TOLERANCE_MINUTES)
        end_window = now + timedelta(hours=12)

        shift = await self.repository.get_planned_shift_in_window(user_id, start_window, end_window)

        if not shift:
            raise Exception("Nenhum plantão planejado encontrado para agora.")

        shift.checkin_time = now
        shift.checkin_lat = lat
        shift.checkin_long = long
        shift.status = ShiftStatus.IN_PROGRESS

        if not shift.user_timesheet_id:
            await self._ensure_timesheet_link(shift)

        await self.repository.update_user_shift(shift)
        return {"status": "success", "time": now}

    async def perform_checkout(self, user_id: UUID) -> dict:
        """
        Fecha o plantão e calcula valores preliminares.
        """
        now = datetime.now()
        shift = await self.repository.get_in_progress_shift(user_id)

        if not shift:
            raise Exception("Erro: Plantão não iniciado.")

        shift.checkout_time = now
        shift.status = ShiftStatus.COMPLETED

        if shift.checkin_time:
            duration = shift.checkout_time - shift.checkin_time
            shift.hours_worked = round(duration.total_seconds() / 3600, 2)

        shift.final_value = shift.agreed_value

        await self.repository.update_user_shift(shift)
        if shift.user_timesheet_id:
            await self.user_timesheet_service.update_has_shifts_stats(shift.user_timesheet_id)

        return {"status": "closed", "hours": shift.hours_worked}

    async def get_shifts_by_filter(
        self,
        institution_id: UUID,
        year_month: str,
        user_id: UUID | None = None,
        sector_id: UUID | None = None,
    ) -> list[UserShiftsBySectorResponse]:
        """Get shifts filtered by institution, year-month, user and sector."""
        shifts = await self.repository.get_shifts_by_filter(
            institution_id, year_month, user_id, sector_id
        )

        grouped_shifts: dict[UUID, list[UserShift]] = {}
        sectors_map: dict[UUID, SectorSimpleResponse] = {}

        for shift in shifts:
            if not shift.shift or not shift.shift.sector:
                continue

            sector = shift.shift.sector
            if sector.id not in sectors_map:
                sectors_map[sector.id] = SectorSimpleResponse.model_validate(sector)
                grouped_shifts[sector.id] = []

            grouped_shifts[sector.id].append(shift)

        response: list[UserShiftsBySectorResponse] = []
        for sector_id, sector_info in sectors_map.items():
            response.append(
                UserShiftsBySectorResponse(
                    sector=sector_info,
                    shifts=[UserShiftResponse.model_validate(s) for s in grouped_shifts[sector_id]],
                )
            )

        return response

    async def get_shift_with_details(self, shift_id: UUID) -> UserShiftDetailResponse | None:
        """Get shift with details."""
        return await self.repository.get_shift_with_details(shift_id)

    async def update_shift(self, shift_id: UUID, update_data: "UserShiftUpdate") -> UserShift:
        """Update a user shift and potentially the slot configuration."""
        shift = await self.repository.get_by_id(shift_id)
        if not shift:
            raise NotFoundException("Plantão de usuário não encontrado")

        data = update_data.model_dump(exclude_unset=True)

        current_user_id = shift.user_id
        current_assistance_id = shift.assistance_user_id
        old_timesheet_id = shift.user_timesheet_id

        self._apply_direct_fields(shift, data)

        if "needs_assistance" in data and data["needs_assistance"] is False:
            await self.revert_shift_coverage(shift)

        if "user_id" in data and shift.user_id is not None and shift.status == ShiftStatus.OPEN:
            shift.status = ShiftStatus.PLANNED

        await self._apply_fixed_professional_fields(shift, data)

        if "user_id" in data or "assistance_user_id" in data:
            await self._ensure_timesheet_link(shift, persist=False)

        await self._create_shift_exchange_if_needed(shift, current_user_id, current_assistance_id)

        updated_shift = await self.repository.update_user_shift(shift)

        await self._update_timesheet_stats_after_shift_change(
            old_timesheet_id, updated_shift.user_timesheet_id, data
        )

        return updated_shift

    @staticmethod
    def _apply_direct_fields(shift: UserShift, data: dict) -> None:
        """Aplica campos editáveis diretamente no shift."""
        direct_fields = [
            "user_id",
            "checkin_time",
            "checkout_time",
            "checkin_lat",
            "checkin_long",
            "status",
            "agreed_value",
            "notes",
            "assistance_user_id",
            "needs_assistance",
            "assistance_reason",
        ]
        for field in direct_fields:
            if field in data:
                setattr(shift, field, data[field])

    async def _apply_fixed_professional_fields(self, shift: UserShift, data: dict) -> None:
        """Verifica e aplica atualizações de profissional fixo no slot config."""
        fixed_fields_map = {
            "is_fixed_professional": "is_fixed",
            "fixed_user_id": "fixed_user_id",
        }
        has_fixed_update = any(field in data for field in fixed_fields_map)
        if has_fixed_update and shift.slot_config_id:
            await self._handle_fixed_professional_update(shift, data, fixed_fields_map)

    async def _create_shift_exchange_if_needed(
        self,
        shift: UserShift,
        previous_user_id: UUID | None,
        previous_assistance_id: UUID | None,
    ) -> None:
        """Cria registro de troca de plantão se houve mudança de usuário."""
        exchange_old_person_id, exchange_target_id = self._detect_exchange_change(
            shift.user_id,
            previous_user_id,
            shift.assistance_user_id,
            previous_assistance_id,
        )
        if exchange_old_person_id is None and exchange_target_id is None:
            return

        exchange = ShiftExchange(
            requester_shift_id=shift.id,
            target_user_id=exchange_target_id,
            old_person_id=exchange_old_person_id,
            status=ShiftExchangeStatusEnum.APPROVED,
        )
        self.repository.db.add(exchange)
        await self.repository.db.flush()

    @staticmethod
    def _detect_exchange_change(
        new_user_id: UUID | None,
        old_user_id: UUID | None,
        new_assistance_id: UUID | None,
        old_assistance_id: UUID | None,
    ) -> tuple[UUID | None, UUID | None]:
        """Retorna (old_person_id, target_id) se houve troca, senão (None, None)."""
        if new_user_id != old_user_id:
            if new_user_id:
                return old_user_id, new_user_id
            if old_user_id:
                return old_user_id, None

        elif new_assistance_id != old_assistance_id:
            if new_assistance_id:
                return old_assistance_id, new_assistance_id
            if old_assistance_id:
                return old_assistance_id, None

        return None, None

    async def _update_timesheet_stats_after_shift_change(
        self,
        old_timesheet_id: UUID | None,
        new_timesheet_id: UUID | None,
        data: dict,
    ) -> None:
        """Atualiza estatísticas dos timesheets afetados pela mudança."""
        if old_timesheet_id != new_timesheet_id:
            if old_timesheet_id:
                await self.user_timesheet_service.update_has_shifts_stats(old_timesheet_id)
            if new_timesheet_id:
                await self.user_timesheet_service.update_has_shifts_stats(new_timesheet_id)
        elif "agreed_value" in data and new_timesheet_id:
            await self.user_timesheet_service.update_has_shifts_stats(new_timesheet_id)

    async def _handle_fixed_professional_update(  # noqa: C901
        self, shift: UserShift, data: dict, fixed_fields_map: dict
    ) -> None:
        """Handle updates related to fixed professional configuration."""
        from app.api.models.shifts import ShiftSlotConfig

        slot_config = await self.repository.db.get(ShiftSlotConfig, shift.slot_config_id)
        if not slot_config:
            return

        should_propagate = False
        should_clear = False

        if "is_fixed_professional" in data:
            new_is_fixed = data["is_fixed_professional"]

            if new_is_fixed != slot_config.is_fixed:
                slot_config.is_fixed = new_is_fixed
                if new_is_fixed:
                    if "fixed_user_id" not in data:
                        slot_config.fixed_user_id = shift.user_id
                    should_propagate = True
                else:
                    slot_config.fixed_user_id = None
                    should_clear = True

            elif new_is_fixed:
                if "user_id" in data and "fixed_user_id" not in data:
                    if slot_config.fixed_user_id != data["user_id"]:
                        slot_config.fixed_user_id = data["user_id"]
                        should_propagate = True

        if "fixed_user_id" in data:
            new_user_id = data["fixed_user_id"]
            if new_user_id != slot_config.fixed_user_id:
                slot_config.fixed_user_id = new_user_id

                if "is_fixed_professional" not in data and new_user_id is not None:
                    slot_config.is_fixed = True

                if slot_config.is_fixed:
                    should_propagate = True

        if should_propagate and slot_config.is_fixed and slot_config.fixed_user_id:
            query_fixed = select(UserShift).where(
                UserShift.shift_id == shift.shift_id,
                UserShift.slot_config_id == slot_config.id,
                UserShift.date >= dt_date.today(),
                UserShift.status.in_([ShiftStatus.OPEN, ShiftStatus.PLANNED]),
            )
            result_fixed = await self.repository.db.execute(query_fixed)
            future_shifts_fixed = result_fixed.scalars().all()

            for future_shift in future_shifts_fixed:
                if future_shift.id != shift.id:
                    future_shift.user_id = slot_config.fixed_user_id
                    if future_shift.user_id:
                        future_shift.status = ShiftStatus.PLANNED
                        await self._ensure_timesheet_link(future_shift, persist=False)
                    else:
                        future_shift.status = ShiftStatus.OPEN
                        future_shift.user_timesheet_id = None

        elif should_clear:
            query_unfix = select(UserShift).where(
                UserShift.shift_id == shift.shift_id,
                UserShift.slot_config_id == slot_config.id,
                UserShift.date >= dt_date.today(),
                UserShift.status.in_([ShiftStatus.OPEN, ShiftStatus.PLANNED]),
            )
            result_unfix = await self.repository.db.execute(query_unfix)
            future_shifts_unfix = result_unfix.scalars().all()

            for future_shift in future_shifts_unfix:
                if future_shift.id != shift.id:
                    future_shift.user_id = None
                    future_shift.user_timesheet_id = None
                    future_shift.status = ShiftStatus.OPEN

    async def cancel_shift(self, shift_id: UUID) -> UserShiftResponse:
        """Cancel a user shift."""
        shift = await self.repository.get_by_id(shift_id)
        if not shift:
            raise NotFoundException("Plantão de usuário não encontrado")

        shift.status = ShiftStatus.CANCELED
        await self.repository.update_user_shift(shift)
        return UserShiftResponse.model_validate(shift)

    async def create_or_update_shift_exchange(
        self, shift_id: UUID, exchange_data: ShiftExchangeCreate
    ) -> ShiftExchangeResponse:
        """Handle creation or update of shift exchange."""
        shift = await self.repository.get_by_id(shift_id)
        if not shift:
            raise NotFoundException("Plantão de usuário não encontrado")

        if not shift.user_id:
            raise BadRequestException("Plantão não tem usuário atribuído para troca.")

        original_user_id = shift.user_id
        new_user_id = exchange_data.target_user_id

        # Fetch shift with institution and sector to get IDs for timesheet
        shift_with_details = await self.repository.get_shift_with_institution_and_sector(shift.id)
        if not shift_with_details or not shift_with_details.shift:
            raise NotFoundException("Detalhes do plantão não encontrados")

        institution_id = shift_with_details.shift.institution_id
        sector_id = shift_with_details.shift.sector_id
        ref_date = shift.date or shift.planned_start.date()

        if not new_user_id:
            raise BadRequestException("Usuário de destino é obrigatório para troca de plantão.")

        new_user_timesheet = await self.user_timesheet_service.find_or_create_open_user_timesheet(
            new_user_id, institution_id, sector_id, ref_date
        )

        shift.user_timesheet_id = new_user_timesheet.id
        shift.assistance_user_id = new_user_id

        await self.repository.update_user_shift(shift)

        data = exchange_data.model_dump(exclude_unset=True)

        exchange = ShiftExchange(
            requester_shift_id=shift.id,
            target_user_id=new_user_id,
            old_person_id=original_user_id,
            manager_notes=data.get("manager_notes"),
            status=ShiftExchangeStatusEnum.APPROVED,
        )
        self.repository.db.add(exchange)
        await self.repository.db.flush()

        # Fetch with relationship
        query = (
            select(ShiftExchange)
            .options(selectinload(ShiftExchange.target_user))
            .options(selectinload(ShiftExchange.old_person))
            .where(ShiftExchange.id == exchange.id)
        )
        result = await self.repository.db.execute(query)
        created_exchange = result.scalar_one()

        return ShiftExchangeResponse.model_validate(created_exchange)

    async def bulk_assign_user(self, request: BulkAssignRequest) -> list[UserShiftResponse]:
        """
        Assign user to multiple shifts based on strategy.
        """
        if not request.shift_id and not request.shift_type_id:
            raise NotFoundException("Deve informar shift_id ou shift_type_id")

        candidates = await self.repository.get_candidate_shifts_for_bulk(
            request.start_date,
            request.end_date,
            sector_id=request.sector_id,
            shift_id=request.shift_id,
            shift_type_id=request.shift_type_id,
        )

        if not candidates:
            raise NotFoundException("Nenhum plantão disponível para o usuário")

        assigned_shifts: list[UserShift] = []
        assigned_dates: set[dt_date] = set()

        if request.strategy == AssignmentStrategy.EVERY_DAY:
            await self.assign_every_day(
                candidates, request.user_id, assigned_shifts, assigned_dates
            )
        elif request.strategy == AssignmentStrategy.ALTERNATING_DAYS:
            await self.assign_alternating_days(
                candidates, request.user_id, assigned_shifts, assigned_dates
            )
        elif request.strategy == AssignmentStrategy.WORK_12_REST_36:
            await self.assign_12x36(candidates, request.user_id, assigned_shifts, assigned_dates)

        for shift in assigned_shifts:
            await self.repository.update_user_shift(shift)

        return [UserShiftResponse.model_validate(s) for s in assigned_shifts]

    async def assign_every_day(
        self,
        candidates: list[UserShift],
        user_id: UUID,
        assigned_shifts: list[UserShift],
        assigned_dates: set[dt_date],
    ) -> None:
        """Assign user to every day available."""
        for shift in candidates:
            if shift.date in assigned_dates:
                continue
            shift.user_id = user_id
            shift.status = ShiftStatus.PLANNED
            await self._ensure_timesheet_link(shift, persist=False)
            assigned_shifts.append(shift)
            assigned_dates.add(shift.date)

    async def assign_alternating_days(
        self,
        candidates: list[UserShift],
        user_id: UUID,
        assigned_shifts: list[UserShift],
        assigned_dates: set[dt_date],
    ) -> None:
        """Assign user to alternating days (day on, day off)."""
        last_date = None
        for shift in candidates:
            if shift.date in assigned_dates:
                continue

            if last_date is None:
                shift.user_id = user_id
                shift.status = ShiftStatus.PLANNED
                await self._ensure_timesheet_link(shift, persist=False)
                assigned_shifts.append(shift)
                assigned_dates.add(shift.date)
                last_date = shift.date
            else:
                days_diff = (shift.date - last_date).days
                if days_diff >= 2:
                    shift.user_id = user_id
                    shift.status = ShiftStatus.PLANNED
                    await self._ensure_timesheet_link(shift, persist=False)
                    assigned_shifts.append(shift)
                    assigned_dates.add(shift.date)
                    last_date = shift.date

    async def assign_12x36(
        self,
        candidates: list[UserShift],
        user_id: UUID,
        assigned_shifts: list[UserShift],
        assigned_dates: set[dt_date],
    ) -> None:
        """Assign user to 12x36 schedule."""
        last_end = None
        for shift in candidates:
            if shift.date in assigned_dates:
                continue

            if last_end is None:
                shift.user_id = user_id
                shift.status = ShiftStatus.PLANNED
                await self._ensure_timesheet_link(shift, persist=False)
                assigned_shifts.append(shift)
                assigned_dates.add(shift.date)
                last_end = shift.planned_end
            else:
                if shift.planned_start >= last_end + timedelta(hours=36):
                    shift.user_id = user_id
                    shift.status = ShiftStatus.PLANNED
                    await self._ensure_timesheet_link(shift, persist=False)
                    assigned_shifts.append(shift)
                    assigned_dates.add(shift.date)
                    last_end = shift.planned_end

        for shift in assigned_shifts:
            await self.repository.update_user_shift(shift)

    async def revert_shift_coverage(self, shift: UserShift) -> None:
        """
        Reverte a cobertura do plantão, voltando o timesheet para o usuário original.
        """
        if not shift.user_id:
            return

        shift_with_details = await self.repository.get_shift_with_institution_and_sector(shift.id)
        if not shift_with_details or not shift_with_details.shift:
            return

        institution_id = shift_with_details.shift.institution_id
        sector_id = shift_with_details.shift.sector_id
        ref_date = shift.date or shift.planned_start.date()

        original_user_timesheet = (
            await self.user_timesheet_service.find_or_create_open_user_timesheet(
                shift.user_id, institution_id, sector_id, ref_date
            )
        )

        shift.user_timesheet_id = original_user_timesheet.id
        shift.assistance_user_id = None
        await self.repository.update_user_shift(shift)
