"""Shift Type Service."""

from collections.abc import Sequence
from uuid import UUID

from fastapi import Depends, HTTPException

from app.api.models.shift_types import ShiftType
from app.api.repositories.shift_type_repository import ShiftTypeRepository
from app.api.repositories.shift_repository import ShiftRepository
from app.api.schemas.shift_types import ShiftTypeCreate, ShiftTypeResponse, ShiftTypeUpdate


class ShiftTypeService:
    """Shift Type Service."""

    def __init__(
        self,
        repository: ShiftTypeRepository = Depends(ShiftTypeRepository),
        shift_repository: ShiftRepository = Depends(ShiftRepository),
    ):
        self.repository = repository
        self.shift_repository = shift_repository

    async def create_shift_type(self, type_create: ShiftTypeCreate) -> ShiftTypeResponse:
        """Create a new shift type."""
        shift_type = ShiftType(**type_create.model_dump())
        created_type = await self.repository.create(shift_type)
        return ShiftTypeResponse.model_validate(created_type)

    async def update_shift_type(
        self, type_id: UUID, type_update: ShiftTypeUpdate
    ) -> ShiftTypeResponse | None:
        """Update a shift type."""
        updated_type = await self.repository.update(type_id, type_update)
        if updated_type:
            return ShiftTypeResponse.model_validate(updated_type)
        return None

    async def list_shift_types(
        self, institution_id: UUID | None = None, include_deleted: bool = False
    ) -> Sequence[ShiftTypeResponse]:
        """List all shift types (optionally filtered by institution)."""
        print(include_deleted)
        if institution_id:
            types = await self.repository.get_types_by_institution_id(
                institution_id, include_deleted
            )
        else:
            types = await self.repository.get_all(include_deleted)
        return [ShiftTypeResponse.model_validate(t) for t in types]

    async def get_shift_type(
        self, type_id: UUID, include_deleted: bool = False
    ) -> ShiftTypeResponse | None:
        """Get a shift type by ID."""
        shift_type = await self.repository.get_by_id(type_id, include_deleted)
        if shift_type:
            return ShiftTypeResponse.model_validate(shift_type)
        return None

    async def delete_shift_type(self, type_id: UUID) -> None:
        """Delete a shift type."""
        shift_type = await self.get_shift_type(type_id)
        if not shift_type:
            raise HTTPException(status_code=404, detail="Shift type not found")
        has_active = await self.shift_repository.has_active_shifts_by_type(type_id)
        if has_active:
            raise HTTPException(
                status_code=400,
                detail="Não é possível excluir este tipo de turno pois existem turnos ativos vinculados a ele.",
            )

        await self.repository.delete(type_id)
