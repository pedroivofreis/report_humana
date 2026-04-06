from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, UploadFile

from app.api.schemas.user_timesheets import (
    ShiftsSummaryByUserSectorResponse,
    UserTimesheetDetailResponse,
    UserTimesheetResponse,
    UserTimesheetStatusUpdate,
)
from app.api.services.user_timesheet_service import UserTimesheetService

router = APIRouter()


@router.get("/summary", response_model=list)
async def get_shifts_summary_by_user_sector(
    competence_date: str = Query(..., description="Competence date (required, format: YYYY-MM)"),
    user_id: UUID | None = Query(None, description="Filter by user ID"),
    sector_ids: list[UUID] | None = Query(None, description="Filter by sector IDs (one or more)"),
    service: UserTimesheetService = Depends(UserTimesheetService),
) -> list[ShiftsSummaryByUserSectorResponse]:
    """
    Get shifts summary grouped by user and sector.

    Returns a flat list where each row represents one user-sector combination with:
    - User information
    - Sector and institution details
    - Planned vs accomplished counts and values
    - Timesheet status if exists

    Includes shifts without timesheet (status OPEN).
    """
    summary = await service.get_shifts_summary_by_user_sector(
        competence_date=competence_date,
        user_id=user_id,
        sector_ids=sector_ids,
    )

    return [ShiftsSummaryByUserSectorResponse(**item) for item in summary]


@router.get("/summary/{user_timesheet_id}", response_model=UserTimesheetDetailResponse)
async def get_user_timesheet_with_details(
    user_timesheet_id: UUID,
    service: UserTimesheetService = Depends(UserTimesheetService),
) -> UserTimesheetDetailResponse:
    """
    Get a single timesheet by ID with complete details including:
    - Professional (user) data
    - Sector information
    - Institution information
    - User shifts
    """
    timesheet = await service.get_user_timesheet_with_details(user_timesheet_id)

    if not timesheet:
        raise HTTPException(status_code=404, detail="Folha de ponto não encontrada")

    return UserTimesheetDetailResponse.model_validate(timesheet)


@router.get("/groups/{user_timesheet_id}", response_model=UserTimesheetResponse)
async def read_user_timesheet(
    user_timesheet_id: UUID,
    service: UserTimesheetService = Depends(UserTimesheetService),
) -> UserTimesheetResponse:
    user_timesheet = await service.get_user_timesheet(user_timesheet_id)
    if user_timesheet is None:
        raise HTTPException(status_code=404, detail="Folha de ponto do usuário não encontrada")
    return user_timesheet


@router.post("/import")
async def import_timesheet(
    background_tasks: BackgroundTasks,
    user_timesheet_id: UUID = Query(..., description="User Timesheet ID"),
    file: UploadFile = File(...),
    service: UserTimesheetService = Depends(UserTimesheetService),
) -> dict[str, str]:
    """
    Import timesheet file (image/pdf), upload to S3, and process in background.
    """
    s3_key = await service.upload_timesheet_file(user_timesheet_id, file)

    background_tasks.add_task(service.process_timesheet_background, user_timesheet_id, s3_key)

    return {"message": "Escala importada e processamento iniciado"}


@router.put("/{user_timesheet_id}/status", response_model=UserTimesheetDetailResponse)
async def update_timesheet_status(
    user_timesheet_id: UUID,
    status_update: UserTimesheetStatusUpdate,
    service: UserTimesheetService = Depends(UserTimesheetService),
) -> UserTimesheetDetailResponse:
    """
    Update timesheet status (Approve/Reject).
    Required current status: PLANNED, PROCESSING, IN_ANALYSIS, REPROVED.
    Updates to RELEASED (Approve) will complete all shifts.
    """

    await service.update_status(user_timesheet_id, status_update)

    timesheet_details = await service.get_user_timesheet_with_details(user_timesheet_id)
    return UserTimesheetDetailResponse.model_validate(timesheet_details)
