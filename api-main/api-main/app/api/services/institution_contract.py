"""Institution Contract service."""

from uuid import UUID

from fastapi import Depends, HTTPException

from app.api.models.institution_contract import InstitutionContract
from app.api.repositories.institution_contract import InstitutionContractRepository
from app.api.schemas.institution_contract import (
    InstitutionContractCreate,
    InstitutionContractUpdate,
)


class InstitutionContractService:
    """Institution Contract service."""

    def __init__(
        self, repository: InstitutionContractRepository = Depends(InstitutionContractRepository)
    ) -> None:
        self.repository = repository

    async def create_contract(self, data: InstitutionContractCreate) -> InstitutionContract:
        """Create a new institution contract."""
        contract = InstitutionContract(**data.model_dump())
        return await self.repository.create(contract)

    async def get_contract(self, contract_id: UUID) -> InstitutionContract:
        """Get a specific contract."""
        contract = await self.repository.get_with_details(contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Institution contract not found")
        return contract

    async def get_all_contracts(self) -> list[InstitutionContract]:
        """Get all contracts."""
        return await self.repository.get_all_with_details()

    async def get_contracts_by_institution(self, institution_id: UUID) -> list[InstitutionContract]:
        """Get all contracts for a specific institution."""
        return await self.repository.get_by_institution(institution_id)

    async def update_contract(
        self, contract_id: UUID, data: InstitutionContractUpdate
    ) -> InstitutionContract:
        """Update an existing contract."""
        contract = await self.repository.get_by_id(contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Institution contract not found")

        update_data = data.model_dump(exclude_unset=True)
        updated_contract = await self.repository.update(contract_id, update_data)
        if not updated_contract:
            raise HTTPException(status_code=400, detail="Failed to update contract")

        return await self.get_contract(contract_id)

    async def delete_contract(self, contract_id: UUID) -> None:
        """Delete a contract."""
        contract = await self.repository.get_by_id(contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Institution contract not found")

        await self.repository.delete(contract_id)
