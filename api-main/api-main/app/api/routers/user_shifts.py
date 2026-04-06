from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.models.user_shifts import UserShift
from app.api.schemas.user_shifts import (
    BulkAssignRequest,
    ShiftExchangeCreate,
    ShiftExchangeResponse,
    UserShiftCreate,
    UserShiftDetailResponse,
    UserShiftResponse,
    UserShiftsBySectorResponse,
    UserShiftUpdate,
)
from app.api.services.user_shift_service import UserShiftService
from app.core.exceptions import BadRequestException, NotFoundException

router = APIRouter()


@router.post(
    "/bulk-assign",
    response_model=list[UserShiftResponse],
    status_code=200,
    summary="Bulk Assign User Shifts",
    description="Assigns a user to multiple shifts based on a selected strategy (e.g., Every Day, 12x36).",
)
async def bulk_assign_user_shifts(
    request: BulkAssignRequest, service: UserShiftService = Depends(UserShiftService)
) -> list[UserShiftResponse]:
    """
    Bulk assign user to shifts.
    """
    return await service.bulk_assign_user(request)


@router.post(
    "",
    response_model=UserShiftResponse,
    status_code=201,
    summary="Create Planned User Shift",
    description="Creates a new planned shift instance. If a user is provided, it automatically links to their monthly timesheet.",
)
async def create_user_shift(
    shift: UserShiftCreate, service: UserShiftService = Depends()
) -> UserShiftResponse:
    try:
        user_shift = UserShift(**shift.model_dump())
        return await service.create_planned_shift(user_shift)
    except Exception as e:
        raise BadRequestException(message=str(e)) from e


@router.get(
    "",
    response_model=list[UserShiftsBySectorResponse],
    status_code=200,
    summary="Get User Shifts",
    description="Get shifts filtered by institution, competence date (YYYY-MM) and optional user. Returns shifts grouped by sector.",
)
async def get_user_shifts(
    institution_id: UUID = Query(..., description="Institution ID"),
    competence: str = Query(
        ..., description="Competence (YYYY-MM)", regex=r"^\d{4}-\d{2}$", alias="date"
    ),
    user_id: UUID | None = Query(None, description="User ID (optional)"),
    sector_id: UUID | None = Query(None, description="Sector ID (optional)"),
    service: UserShiftService = Depends(),
) -> list[UserShiftsBySectorResponse]:
    try:
        return await service.get_shifts_by_filter(institution_id, competence, user_id, sector_id)
    except Exception as e:
        raise BadRequestException(message=str(e)) from e


@router.get(
    "/{shift_id}",
    response_model=UserShiftDetailResponse,
    status_code=200,
    summary="Get User Shift by ID",
    description="Get user shift by ID with shift template details.",
)
async def get_user_shift_by_id(
    shift_id: UUID,
    service: UserShiftService = Depends(),
) -> UserShiftDetailResponse:
    result = await service.get_shift_with_details(shift_id)
    if not result:
        raise NotFoundException(message="Plantão de usuário não encontrado")
    return result


@router.put(
    "/{shift_id}",
    response_model=UserShiftResponse,
    summary="Update User Shift",
    description="Updates user shift details. Can also configure fixed professional settings for the underlying slot.",
)
async def update_shift(
    shift_id: UUID,
    update_data: UserShiftUpdate,
    service: UserShiftService = Depends(),
) -> UserShiftResponse:
    try:
        return await service.update_shift(shift_id, update_data)
    except Exception as e:
        raise BadRequestException(message=str(e)) from e


@router.post(
    "/{shift_id}/exchange",
    response_model=ShiftExchangeResponse,
    status_code=200,
    summary="Create or Update Shift Exchange",
    description="Creates or updates a shift exchange request for the given shift.",
)
async def create_or_update_shift_exchange(
    shift_id: UUID,
    exchange_data: ShiftExchangeCreate,
    service: UserShiftService = Depends(),
) -> ShiftExchangeResponse:
    try:
        return await service.create_or_update_shift_exchange(shift_id, exchange_data)
    except Exception as e:
        raise BadRequestException(message=str(e)) from e


@router.post(
    "/checkin/{user_id}",
    response_model=UserShiftResponse,
    status_code=201,
    summary="Perform Check-in",
    description="Registers the start of a shift for a user. Validates geolocation and time window tolerance.",
)
async def checkin(
    user_id: UUID,
    lat: float,
    long: float,
    service: UserShiftService = Depends(),
) -> dict[str, Any]:
    try:
        return await service.perform_checkin(user_id, lat, long)
    except Exception as e:
        raise BadRequestException(message=str(e)) from e


@router.post(
    "/checkout/{user_id}",
    response_model=UserShiftResponse,
    status_code=201,
    summary="Perform Check-out",
    description="Registers the end of a shift, calculates worked hours, and updates the status to COMPLETED.",
)
async def checkout(
    user_id: UUID,
    service: UserShiftService = Depends(),
) -> dict[str, Any]:
    try:
        return await service.perform_checkout(user_id)
    except Exception as e:
        raise BadRequestException(message=str(e)) from e


@router.post(
    "/{shift_id}/cancel",
    response_model=UserShiftResponse,
    status_code=200,
    summary="Cancel User Shift",
    description="Cancels a user shift by setting its status to CANCELED.",
)
async def cancel_shift(
    shift_id: UUID,
    service: UserShiftService = Depends(),
) -> UserShiftResponse:
    try:
        return await service.cancel_shift(shift_id)
    except Exception as e:
        raise BadRequestException(message=str(e)) from e
