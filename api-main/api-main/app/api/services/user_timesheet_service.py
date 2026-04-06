"""User Timesheet service module."""

from datetime import date, datetime
from typing import Any
from uuid import UUID

from fastapi import Depends, UploadFile

from app.api.models.user_shifts import ShiftStatus
from app.api.models.user_timesheets import TimesheetStatus, UserTimesheet
from app.api.repositories.user_timesheet_repository import UserTimesheetRepository
from app.api.schemas.user_timesheets import UserTimesheetStatusUpdate
from app.core.exceptions import BadRequestException


class UserTimesheetService:
    """
    Service for managing User Timesheets
    """

    def __init__(
        self,
        repository: UserTimesheetRepository = Depends(UserTimesheetRepository),
    ):
        self.repository = repository

    async def find_or_create_open_user_timesheet(
        self, user_id: UUID, institution_id: UUID, sector_id: UUID, date_obj: date | datetime
    ) -> UserTimesheet:
        """
        Encontra um UserTimesheet aberto para o usuário/mês ou cria um novo.
        """
        competence = date_obj.strftime("%Y-%m")
        user_timesheet = await self.repository.get_by_user_and_competence(user_id, competence)

        if not user_timesheet:
            user_timesheet = UserTimesheet(
                user_id=user_id,
                institution_id=institution_id,
                sector_id=sector_id,
                competence_date=competence,
                status=TimesheetStatus.PLANNED,
            )
            await self.repository.create_user_timesheet(user_timesheet)

        return user_timesheet

    async def get_user_timesheet(self, user_timesheet_id: UUID) -> UserTimesheet | None:
        """Busca um timesheet pelo ID."""
        return await self.repository.get_user_timesheet(user_timesheet_id)

    async def get_user_timesheet_with_details(
        self, user_timesheet_id: UUID
    ) -> UserTimesheet | None:
        """Busca um timesheet pelo ID com detalhes (user, sector, institution, shifts)."""
        return await self.repository.get_user_timesheet_with_details(user_timesheet_id)

    async def update_has_shifts_stats(self, user_timesheet_id: UUID) -> None:
        """
        Recalcula somatórias de horas e valores do timesheet baseado nos shifts.
        """
        user_timesheet = await self.repository.get_user_timesheet(user_timesheet_id)
        if not user_timesheet:
            return

        total_hours = 0.0
        total_value = 0.0
        total_planned = 0.0
        total_hours_planned = 0.0

        for shift in user_timesheet.shifts:
            total_planned += shift.agreed_value or 0.0
            total_hours_planned += shift.weight * 12 or 0.0

            if shift.status == ShiftStatus.COMPLETED:
                total_hours += shift.hours_worked or 0.0
                total_value += shift.final_value or 0.0

        user_timesheet.total_hours_realized = total_hours
        user_timesheet.total_hours_planned = total_hours_planned
        user_timesheet.total_value_payable = total_value
        user_timesheet.total_value_planned = total_planned
        await self.repository.update_user_timesheet(user_timesheet_id, user_timesheet)

    async def get_shifts_summary_by_user_sector(
        self,
        competence_date: str,
        user_id: UUID | None = None,
        sector_ids: list[UUID] | None = None,
    ) -> list[dict]:
        """
        Get aggregated shifts summary by user and sector in flat list format.
        Each row represents one user-sector combination.
        """
        from collections import defaultdict

        from app.api.models.user_shifts import ShiftStatus
        from app.api.repositories.user_shift_repository import UserShiftRepository

        shift_repo = UserShiftRepository(self.repository.db)

        shifts = await shift_repo.get_shifts_grouped_by_sector(
            competence_date=competence_date,
            user_id=user_id,
            sector_ids=sector_ids,
        )

        groups: dict[tuple[Any, Any], dict[str, Any]] = defaultdict(
            lambda: {
                "user": None,
                "sector": None,
                "institution": None,
                "timesheet": None,
                "shifts": [],
                "planned_count": 0,
                "planned_value": 0.0,
                "accomplished_count": 0,
                "accomplished_value": 0.0,
                "pending_count": 0,
            }
        )

        for shift in shifts:
            if not shift.shift or not shift.shift.sector:
                continue

            user_key = shift.user_id if shift.user_id else "unassigned"
            sector_key = shift.shift.sector_id
            group_key = (user_key, sector_key)

            if groups[group_key]["user"] is None and shift.user:
                groups[group_key]["user"] = shift.user
            if groups[group_key]["sector"] is None:
                groups[group_key]["sector"] = shift.shift.sector
            if groups[group_key]["institution"] is None:
                groups[group_key]["institution"] = shift.shift.institution

            groups[group_key]["shifts"].append(shift)

            groups[group_key]["planned_count"] += 1
            groups[group_key]["planned_value"] += shift.agreed_value or 0.0

            if shift.status == ShiftStatus.COMPLETED:
                groups[group_key]["accomplished_count"] += 1
                groups[group_key]["accomplished_value"] += shift.final_value or 0.0

            if shift.status in [ShiftStatus.OPEN, ShiftStatus.PLANNED, ShiftStatus.IN_PROGRESS]:
                groups[group_key]["pending_count"] += 1

        timesheets = await self.repository.get_timesheets_with_details(
            competence_date=competence_date,
            user_id=user_id,
            sector_ids=sector_ids,
        )

        for ts in timesheets:
            group_key = (ts.user_id, ts.sector_id)
            if group_key in groups:
                groups[group_key]["timesheet"] = ts

        result = []
        for (_user_key, _sector_key), data in groups.items():
            user_name = "Sem Responsável"
            user_id_value = None
            user_crm = None

            if data["user"]:
                user_name = f"{data['user'].first_name} {data['user'].last_name}"
                user_id_value = data["user"].id
                if hasattr(data["user"], "professional_crms") and data["user"].professional_crms:
                    user_crm = data["user"].professional_crms[0].code

            timesheet_id = data["timesheet"].id if data["timesheet"] else None
            timesheet_status = data["timesheet"].status.value if data["timesheet"] else None

            total_shifts = data["planned_count"]
            accomplished = data["accomplished_count"]

            result.append(
                {
                    "competence_date": competence_date,
                    "user_id": user_id_value,
                    "user_name": user_name,
                    "user_crm": user_crm,
                    "sector_id": data["sector"].id,
                    "sector_name": data["sector"].display_name,
                    "institution_id": data["institution"].id,
                    "institution_name": data["institution"].display_name,
                    "timesheet_id": timesheet_id,
                    "timesheet_status": timesheet_status,
                    "planned_count": data["planned_count"],
                    "planned_value": data["planned_value"],
                    "accomplished_count": data["accomplished_count"],
                    "accomplished_value": data["accomplished_value"],
                    "pending_count": data["pending_count"],
                    "shifts_summary": f"{accomplished}/{total_shifts}",
                    "total_value": data["accomplished_value"],
                }
            )

        return result

    async def upload_timesheet_file(self, user_timesheet_id: UUID, file: UploadFile) -> str:
        """
        Upload timesheet file to S3 and update user_timesheet record with the URL.
        Returns the S3 key for background processing.
        """
        import os
        from datetime import datetime

        from app.api.utils.s3 import s3_service

        timestamp = int(datetime.now().timestamp())
        filename = os.path.splitext(file.filename)[0] if file.filename else "timesheet"
        ext = os.path.splitext(file.filename)[1].lower() if file.filename else ".jpg"
        s3_key = f"timesheets/{timestamp}_{filename}{ext}"

        content = await file.read()
        await file.seek(0)

        import io

        file_obj = io.BytesIO(content)

        url = await s3_service.upload_fileobj(file_obj, s3_key, content_type=file.content_type)

        user_timesheet = await self.repository.get_user_timesheet(user_timesheet_id)
        if user_timesheet:
            user_timesheet.url = url
            user_timesheet.status = TimesheetStatus.PROCESSING
            await self.repository.update_user_timesheet(user_timesheet_id, user_timesheet)

        return s3_key

    async def process_timesheet_background(self, user_timesheet_id: UUID, s3_key: str) -> None:
        """
        Process timesheet image in background: download, send to Gemini, extract data, update shifts.
        """
        import os

        import structlog

        from app.api.utils.s3 import s3_service

        logger = structlog.get_logger(__name__)

        try:
            logger.info(
                "Starting background processing for timesheet", timesheet_id=str(user_timesheet_id)
            )
            temp_file_path = s3_service.download_to_tempfile(s3_key)

            try:
                extracted_data_list = await self._process_image_with_gemini(temp_file_path)
                logger.info("Gemini extracted data", data=extracted_data_list)

                if extracted_data_list:
                    await self._apply_extracted_data(user_timesheet_id, extracted_data_list)

            finally:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        except Exception as e:
            logger.error(
                "Error processing timesheet background",
                error=str(e),
                timesheet_id=str(user_timesheet_id),
            )

    async def _process_image_with_gemini(self, image_path: str) -> list[dict]:
        """Call Gemini API to extract data from image."""
        import json

        from google import genai
        from google.genai import types
        from PIL import Image

        from app.api.schemas.ai_extraction import TimesheetImageData
        from app.core.config import settings

        if not settings.GOOGLE_API_KEY:
            raise Exception("GOOGLE_API_KEY not found in settings")

        client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        img = Image.open(image_path)

        prompt = """
        Você é um especialista em extração de dados de imagens de folhas de ponto.
        Analise a imagem cuidadosamente e extraia TODAS as informações presentes.
        Retorne um array com TODOS os objetos JSON válidos com a seguinte estrutura:
        {
            "parent_institutions.display_name": "nome da instituição pai",
            "child_institutions.display_name": "nome da instituição filha",
            "user.first_name": "primeiro nome do usuário",
            "user.last_name": "sobrenome do usuário",
            "user.crm": "número do CRM",
            "Data_Dia": "data no formato YYYY-MM-DD (Exemplo: 2024-02-25). Converta se necessário, mas a saída deve ser YYYY-MM-DD",
            "Entrada_1": "horário de entrada 1 no formato HH:MM ou '-'",
            "Saida_1": "horário de saída 1 no formato HH:MM ou '-'",
            "Entrada_2": "horário de entrada 2 no formato HH:MM ou '-'",
            "Saida_2": "horário de saída 2 no formato HH:MM ou '-'",
            "Carimbo_Assinatura": "true se houver carimbo/assinatura, false caso contrário"
        }
        IMPORTANTE:
        - Retorne APENAS o JSON, sem texto adicional
        - Se campo inexistente, use "-" ou false
        - Datas YYYY-MM-DD, Horários HH:MM
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[str(prompt), img],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )

        cleaned_json = (response.text or "").strip()
        data = json.loads(cleaned_json)

        validated = [TimesheetImageData(**item) for item in data]
        return [item.model_dump(by_alias=True) for item in validated]

    async def _apply_extracted_data(
        self, user_timesheet_id: UUID, extracted_data: list[dict]
    ) -> None:
        """
        Match extracted data with existing shifts and update them.
        """
        from datetime import datetime, timedelta

        import structlog

        from app.api.models.user_shifts import ShiftStatus
        from app.api.repositories.user_shift_repository import UserShiftRepository

        logger = structlog.get_logger(__name__)
        logger.info(
            "Applying extracted data",
            timesheet_id=str(user_timesheet_id),
            items_count=len(extracted_data),
        )

        user_timesheet = await self.repository.get_user_timesheet(user_timesheet_id)
        if not user_timesheet or not user_timesheet.shifts:
            logger.warning(
                "Timesheet not found or has no shifts", timesheet_id=str(user_timesheet_id)
            )
            return

        def to_minutes(hhmm: str) -> int:
            try:
                if not hhmm or hhmm == "-":
                    return -1
                hhmm = hhmm.strip()
                h, m = map(int, hhmm.split(":"))
                return h * 60 + m
            except Exception as e:
                logger.warning("Error parsing time", time_str=hhmm, error=str(e))
                return -1

        shifts_by_date: dict[str, list[Any]] = {}
        for shift in user_timesheet.shifts:
            d_str = shift.date.strftime("%Y-%m-%d")
            shifts_by_date.setdefault(d_str, []).append(shift)
            d_str_br = shift.date.strftime("%d/%m/%Y")
            shifts_by_date.setdefault(d_str_br, []).append(shift)

        logger.info("Available shift dates", dates=list(shifts_by_date.keys()))

        shift_repo = UserShiftRepository(self.repository.db)

        for item in extracted_data:
            date_dia = item.get("Data_Dia")
            logger.info("Processing item", date_dia=date_dia, item=item)

            if date_dia in shifts_by_date:
                start1 = item.get("Entrada_1")
                end1 = item.get("Saida_1")
                # start2 = item.get("Entrada_2") # Not using for now based on logic
                # end2 = item.get("Saida_2") # Not using for now based on logic

                matched_any = False
                for shift in shifts_by_date[date_dia]:
                    if not shift.planned_start:
                        logger.info("Shift has no planned start", shift_id=str(shift.id))
                        continue

                    planned_start_min = shift.planned_start.hour * 60 + shift.planned_start.minute
                    logger.info(
                        "Checking shift", shift_id=str(shift.id), planned_start=shift.planned_start
                    )

                    matched = False

                    s1_min = to_minutes(str(start1 or "-"))
                    if s1_min >= 0:
                        diff = abs(planned_start_min - s1_min)
                        logger.info(
                            "Time diff check", planned=planned_start_min, actual=s1_min, diff=diff
                        )

                        if diff <= 60:
                            matched = True
                            shift.checkin_time = datetime.combine(
                                shift.date, datetime.min.time()
                            ) + timedelta(minutes=s1_min)

                            e1_min = to_minutes(str(end1 or "-"))
                            if e1_min >= 0:
                                shift.checkout_time = datetime.combine(
                                    shift.date, datetime.min.time()
                                ) + timedelta(minutes=e1_min)
                                duration_minutes = e1_min - s1_min
                                if duration_minutes < 0:  # night shift crossing midnight?
                                    duration_minutes += 24 * 60

                                shift.hours_worked = round(duration_minutes / 60, 2)

                    if matched:
                        matched_any = True
                        shift.status = ShiftStatus.COMPLETED
                        shift.final_value = shift.agreed_value
                        logger.info(
                            "Match found! Updating shift",
                            shift_id=str(shift.id),
                            new_status="COMPLETED",
                        )
                        await shift_repo.update_user_shift(shift)
                    else:
                        logger.info("No match for this shift", shift_id=str(shift.id))

                if not matched_any:
                    logger.warning(
                        "Date matched but no shift time matched within tolerance", date=date_dia
                    )
            else:
                logger.warning("Date not found in user shifts", date=date_dia)

        await self.update_has_shifts_stats(user_timesheet_id)

        user_timesheet = await self.repository.get_user_timesheet(user_timesheet_id)
        if user_timesheet:
            user_timesheet.status = TimesheetStatus.IN_ANALYSIS
            await self.repository.update_user_timesheet(user_timesheet_id, user_timesheet)

    async def update_status(
        self, user_timesheet_id: UUID, status_update: UserTimesheetStatusUpdate
    ) -> UserTimesheet:
        """
        Update timesheet status (Approve/Reject).
        """

        user_timesheet = await self.repository.get_user_timesheet(user_timesheet_id)
        if not user_timesheet:
            raise BadRequestException("Escala não encontrada")

        allowed_statuses = [
            TimesheetStatus.PLANNED,
            TimesheetStatus.PROCESSING,
            TimesheetStatus.IN_ANALYSIS,
            TimesheetStatus.REPROVED,
        ]

        if user_timesheet.status not in allowed_statuses:
            raise BadRequestException(
                f"O status '{user_timesheet.status.value}' não permite atualização."
            )

        if status_update.status == TimesheetStatus.RELEASED:
            from app.api.repositories.user_shift_repository import UserShiftRepository

            shift_repo = UserShiftRepository(self.repository.db)

            for shift in user_timesheet.shifts:
                if shift.status != ShiftStatus.COMPLETED:
                    shift.status = ShiftStatus.COMPLETED
                    if shift.final_value is None or shift.final_value == 0:
                        shift.final_value = shift.agreed_value

                    await shift_repo.update_user_shift(shift)

            user_timesheet.status = TimesheetStatus.RELEASED

            ### Felipe faça sua magica aqui ###

        else:
            user_timesheet.status = TimesheetStatus.REPROVED

        await self.repository.update_user_timesheet(user_timesheet_id, user_timesheet)
        updated = await self.repository.get_user_timesheet(user_timesheet_id)
        if not updated:
            raise BadRequestException("Erro ao atualizar escala")
        return updated
