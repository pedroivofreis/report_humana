"""Address repository."""

import logging
from uuid import UUID

from fastapi import Depends

from app.api.models.address import Address
from app.api.repositories.base import BaseRepository
from app.api.schemas.address import AddressCreateRequest, AddressResponse, AddressUpdateRequest
from app.core.exceptions import ResourceNotFoundException
from app.db.session import AsyncSession, get_db_session

logger = logging.getLogger(__name__)


class AddressRepository(BaseRepository[Address]):
    """Address repository."""

    def __init__(self, db: AsyncSession = Depends(get_db_session)):
        super().__init__(model=Address, db=db)

    async def get_addresses(self, include_deleted: bool = False) -> list[AddressResponse]:
        """Get all addresses."""
        addresses = await self.get_all(include_deleted)
        return [AddressResponse.model_validate(address) for address in addresses]

    async def get_address_by_id(
        self, address_id: UUID, include_deleted: bool = False
    ) -> AddressResponse | None:
        """Get an address by id."""
        address = await self.get_by_id(address_id, include_deleted)
        if not address:
            return None
        return AddressResponse.model_validate(address)

    async def create_address(self, address: AddressCreateRequest) -> AddressResponse:
        """Create an address."""
        new_address = Address(**address.model_dump())
        await self.create(new_address)
        return AddressResponse.model_validate(new_address)

    async def update_address(
        self, address_data: AddressUpdateRequest, address_id: UUID
    ) -> AddressResponse:
        """Update an address."""
        address = await self.get_by_id(address_id)
        if not address:
            raise ResourceNotFoundException(resource_name="address", resource_id=address_id)

        for key, value in address_data.model_dump(exclude_unset=True).items():
            setattr(address, key, value)

        await self.db.commit()
        await self.db.refresh(address)
        return AddressResponse.model_validate(address)

    async def delete_address(self, address_id: UUID) -> None:
        """Delete an address."""
        address = await self.get_by_id(address_id)
        if not address:
            raise ResourceNotFoundException("Endereço não encontrado")
        await self.delete(address_id)
