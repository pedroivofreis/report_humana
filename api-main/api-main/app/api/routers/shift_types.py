"""Shift Type router."""

from collections.abc import Sequence

from fastapi import APIRouter, Depends

from app.api.schemas.shift_types import ShiftTypeCreate, ShiftTypeResponse, ShiftTypeUpdate
from app.api.services.shift_type_service import ShiftTypeService

router = APIRouter(tags=["Shift Types"])


@router.post(
    "",
    response_model=ShiftTypeResponse,
    status_code=201,
    summary="Create Shift Type",
    description="Create a new shift type.",
)
async def create_shift_type(
    shift_type: ShiftTypeCreate,
    service: ShiftTypeService = Depends(),
) -> ShiftTypeResponse:
    """Create a shift type."""
    return await service.create_shift_type(shift_type)


from uuid import UUID

from fastapi import HTTPException


@router.put(
    "/{type_id}",
    response_model=ShiftTypeResponse,
    status_code=200,
    summary="Update Shift Type",
    description="Update a shift type.",
)
async def update_shift_type(
    type_id: UUID,
    shift_type_update: ShiftTypeUpdate,
    service: ShiftTypeService = Depends(),
) -> ShiftTypeResponse:
    """Update a shift type."""
    updated_shift_type = await service.update_shift_type(type_id, shift_type_update)
    if not updated_shift_type:
        raise HTTPException(status_code=404, detail="Shift type not found")
    return updated_shift_type


@router.get(
    "",
    response_model=list[ShiftTypeResponse],
    status_code=200,
    summary="List Shift Types",
    description="List all shift types.",
)
async def list_shift_types(
    institution_id: UUID | None = None,
    active_only: bool = False,
    service: ShiftTypeService = Depends(),
) -> Sequence[ShiftTypeResponse]:
    """List all shift types."""
    return await service.list_shift_types(
        institution_id=institution_id, include_deleted=not active_only
    )


@router.delete(
    "/{type_id}",
    status_code=204,
    summary="Delete Shift Type",
    description="Delete a shift type.",
)
async def delete_shift_type(
    type_id: UUID,
    service: ShiftTypeService = Depends(),
) -> None:
    """Delete a shift type."""
    await service.delete_shift_type(type_id)
