from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.schemas.shifts import ShiftCreate, ShiftResponse, ShiftUpdate
from app.api.services.shift_service import ShiftService
from app.core.exceptions import BadRequestException, NotFoundException

router = APIRouter()


@router.post(
    "",
    response_model=ShiftResponse,
    status_code=201,
    summary="Create Shift",
    description="Creates a new shift (e.g., 'Night Shift UTI') defining rules like duration, value, and type.",
)
async def create_shift(
    shift: ShiftCreate, service: ShiftService = Depends(ShiftService)
) -> ShiftResponse:
    return await service.create_shift(shift)


@router.get(
    "",
    response_model=list[ShiftResponse],
    status_code=200,
    summary="Get All Shifts",
    description="Retrieves a list of all shifts.",
)
async def get_all_shifts(
    service: ShiftService = Depends(ShiftService),
    sector_id: UUID | None = Query(
        default=None, description="ID of the sector to filter shifts", alias="sector_id"
    ),
    institution_id: UUID | None = Query(
        default=None,
        description="ID of the institution to filter shifts",
        alias="institution_id",
    ),
    include_deleted: bool = Query(
        default=False, description="Include deleted shifts", alias="include_deleted"
    ),
) -> list[ShiftResponse]:
    if not sector_id and not institution_id:
        raise BadRequestException(
            message="Deve ser informado o ID do setor ou o ID da instituição."
        )

    return await service.get_all_shifts(
        sector_id=sector_id,
        institution_id=institution_id,
        include_deleted=include_deleted,
    )


@router.get(
    "/{shift_id}",
    response_model=ShiftResponse,
    status_code=200,
    summary="Get Shift",
    description="Retrieves details of a specific shift by its ID.",
)
async def get_shift(shift_id: UUID, service: ShiftService = Depends(ShiftService)) -> ShiftResponse:
    result = await service.get_shift(shift_id)
    if not result:
        raise NotFoundException(message="Plantão não encontrado")
    return result


@router.put(
    "/{shift_id}",
    response_model=ShiftResponse,
    status_code=200,
    summary="Update Shift",
    description="Updates an existing shift. If 'fixed_needs_assistance' is set to True, it triggers logic to assign the reserve professional to future shifts.",
)
async def update_shift(
    shift_id: UUID,
    shift_update: ShiftUpdate,
    service: ShiftService = Depends(ShiftService),
) -> ShiftResponse:
    result = await service.update_shift(shift_id, shift_update)
    if not result:
        raise NotFoundException(message="Plantão não encontrado")
    return result
