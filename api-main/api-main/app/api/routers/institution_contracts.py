"""Institution Contract routes module."""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.schemas.institution_contract import (
    InstitutionContractCreate,
    InstitutionContractResponse,
    InstitutionContractUpdate,
)
from app.api.schemas.institution_contract_sector_value import (
    InstitutionContractSectorValueCreate,
    InstitutionContractSectorValueResponse,
)
from app.api.services.institution_contract import InstitutionContractService
from app.api.services.institution_contract_sector_value import InstitutionContractSectorValueService

router = APIRouter()


@router.post("", response_model=InstitutionContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(
    data: InstitutionContractCreate,
    service: InstitutionContractService = Depends(InstitutionContractService),
) -> InstitutionContractResponse:
    """Create a new institution contract."""
    contract = await service.create_contract(data)
    return await service.get_contract(contract.id)


@router.get("", response_model=list[InstitutionContractResponse])
async def get_all_contracts(
    institution_id: UUID | None = None,
    service: InstitutionContractService = Depends(InstitutionContractService),
) -> list[InstitutionContractResponse]:
    """Get all institution contracts. Optionally filter by institution_id."""
    if institution_id:
        return await service.get_contracts_by_institution(institution_id)
    return await service.get_all_contracts()


@router.get("/{contract_id}", response_model=InstitutionContractResponse)
async def get_contract(
    contract_id: UUID,
    service: InstitutionContractService = Depends(InstitutionContractService),
) -> InstitutionContractResponse:
    """Get a specific institution contract by ID."""
    return await service.get_contract(contract_id)


@router.put("/{contract_id}", response_model=InstitutionContractResponse)
async def update_contract(
    contract_id: UUID,
    data: InstitutionContractUpdate,
    service: InstitutionContractService = Depends(InstitutionContractService),
) -> InstitutionContractResponse:
    """Update an institution contract."""
    return await service.update_contract(contract_id, data)


@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contract(
    contract_id: UUID,
    service: InstitutionContractService = Depends(InstitutionContractService),
) -> None:
    """Delete an institution contract."""
    await service.delete_contract(contract_id)


@router.post(
    "/{contract_id}/sector-values",
    response_model=InstitutionContractSectorValueResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_contract_sector_value(
    contract_id: UUID,
    data: InstitutionContractSectorValueCreate,
    service: InstitutionContractSectorValueService = Depends(InstitutionContractSectorValueService),
) -> InstitutionContractSectorValueResponse:
    """Create a new sector hourly value for an institution contract."""
    return await service.create_sector_value(contract_id, data)


@router.get(
    "/{contract_id}/sector-values",
    response_model=list[InstitutionContractSectorValueResponse],
)
async def get_contract_sector_values(
    contract_id: UUID,
    service: InstitutionContractSectorValueService = Depends(InstitutionContractSectorValueService),
) -> list[InstitutionContractSectorValueResponse]:
    """Get all sector hourly values for an institution contract."""
    return await service.get_values_by_contract(contract_id)


@router.delete(
    "/sector-values/{value_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_contract_sector_value(
    value_id: UUID,
    service: InstitutionContractSectorValueService = Depends(InstitutionContractSectorValueService),
) -> None:
    """Delete a sector hourly value."""
    await service.delete_sector_value(value_id)
