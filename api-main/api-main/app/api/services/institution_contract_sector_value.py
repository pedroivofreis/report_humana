"""Institution Contract Sector Value service."""

from uuid import UUID

from fastapi import Depends, HTTPException

from app.api.models.institution_contract_sector_value import InstitutionContractSectorValue
from app.api.repositories.institution_contract import InstitutionContractRepository
from app.api.repositories.institution_contract_sector_value import (
    InstitutionContractSectorValueRepository,
)
from app.api.schemas.institution_contract_sector_value import InstitutionContractSectorValueCreate


class InstitutionContractSectorValueService:
    """Institution Contract Sector Value service."""

    def __init__(
        self,
        repository: InstitutionContractSectorValueRepository = Depends(
            InstitutionContractSectorValueRepository
        ),
        contract_repository: InstitutionContractRepository = Depends(InstitutionContractRepository),
    ) -> None:
        self.repository = repository
        self.contract_repository = contract_repository

    async def create_sector_value(
        self, contract_id: UUID, data: InstitutionContractSectorValueCreate
    ) -> InstitutionContractSectorValue:
        """Create or update a sector value for a contract.

        If a sector value for the given sector is already active (within
        validity period), updates it. Otherwise creates a new record.
        """
        contract = await self.contract_repository.get_by_id(contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Institution contract not found")

        existing = await self.repository.get_active_by_contract_and_sector(
            contract_id, data.sector_id
        )

        if existing:
            updated = await self.repository.update(existing.id, {"hourly_value": data.hourly_value})
            return await self.repository.get_with_details(updated.id)

        value = InstitutionContractSectorValue(
            institution_contract_id=contract_id,
            sector_id=data.sector_id,
            hourly_value=data.hourly_value,
            start_date=contract.start_date,
            end_date=contract.end_date,
        )

        created = await self.repository.create(value)
        return await self.repository.get_with_details(created.id)

    async def get_values_by_contract(
        self, contract_id: UUID
    ) -> list[InstitutionContractSectorValue]:
        """Get all sector values for a contract."""
        return await self.repository.get_by_contract(contract_id)

    async def delete_sector_value(self, value_id: UUID) -> None:
        """Delete a sector value."""
        value = await self.repository.get_by_id(value_id)
        if not value:
            raise HTTPException(status_code=404, detail="Sector value not found")

        await self.repository.delete(value_id)
