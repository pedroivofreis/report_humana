"""Professional Location Binding router."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.dependencies.authentication import get_current_user
from app.api.models.user import User
from app.api.schemas.professional_location_binding import (
    ProfessionalLocationBindingCreate,
    ProfessionalLocationBindingResponse,
    ProfessionalLocationBindingUpdate,
)
from app.api.services.professional_location_binding import ProfessionalLocationBindingService

router = APIRouter()


@router.post("", response_model=ProfessionalLocationBindingResponse, status_code=201)
async def create_professional_location_binding(
    binding_in: ProfessionalLocationBindingCreate,
    service: ProfessionalLocationBindingService = Depends(),
    current_user: User = Depends(get_current_user),
) -> ProfessionalLocationBindingResponse:
    """Create a new professional location binding."""
    return await service.create_binding(binding_in, current_user.id)


@router.get("/user/{user_id}", response_model=list[ProfessionalLocationBindingResponse])
async def list_professional_location_bindings(
    user_id: UUID,
    service: ProfessionalLocationBindingService = Depends(),
) -> list[ProfessionalLocationBindingResponse]:
    """List professional location bindings."""
    return await service.get_bindings(user_id)


@router.get("/{binding_id}", response_model=ProfessionalLocationBindingResponse)
async def get_professional_location_binding(
    binding_id: UUID,
    service: ProfessionalLocationBindingService = Depends(),
) -> ProfessionalLocationBindingResponse:
    """Get professional location binding by ID."""
    return await service.get_binding_by_id(binding_id)


@router.put("/{binding_id}", response_model=ProfessionalLocationBindingResponse)
async def update_professional_location_binding(
    binding_id: UUID,
    binding_in: ProfessionalLocationBindingUpdate,
    service: ProfessionalLocationBindingService = Depends(),
) -> ProfessionalLocationBindingResponse:
    """Update professional location binding."""
    return await service.update_binding(binding_id, binding_in)


@router.delete("/{binding_id}", status_code=204)
async def delete_professional_location_binding(
    binding_id: UUID,
    service: ProfessionalLocationBindingService = Depends()
) -> None:
    """Delete professional location binding."""
    await service.delete_binding(binding_id)
