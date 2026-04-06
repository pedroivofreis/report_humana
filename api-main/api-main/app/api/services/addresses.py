"""Address service module."""

from uuid import UUID

import structlog
from fastapi import Depends

from app.api.repositories.addresses import AddressRepository
from app.api.schemas.address import AddressCreateRequest, AddressResponse, AddressUpdateRequest
from app.api.validators.address import AddressValidator
from app.core.exceptions import ResourceNotFoundException

logger = structlog.get_logger(__name__)


class AddressService:
    """Address service."""

    def __init__(self, repository: AddressRepository = Depends(AddressRepository)):
        self.repository = repository

    async def get_addresses(self, include_deleted: bool = False) -> list[AddressResponse]:
        """Get all addresses."""
        return await self.repository.get_addresses(include_deleted)

    async def get_address_by_id(
        self, address_id: UUID, include_deleted: bool = False
    ) -> AddressResponse:
        """Get an address by id."""
        address = await self.repository.get_address_by_id(address_id, include_deleted)
        if not address:
            raise ResourceNotFoundException(resource_name="address", resource_id=address_id)
        return address

    async def create_address(self, address: AddressCreateRequest) -> AddressResponse:
        """Create an address."""
        AddressValidator.validate(address)
        return await self.repository.create_address(address)

    async def update_address(
        self, address_id: UUID, address_data: AddressUpdateRequest
    ) -> AddressResponse:
        """Update an address."""
        address = await self.get_address_by_id(address_id)
        if not address:
            raise ResourceNotFoundException(resource_name="address", resource_id=address_id)
        AddressValidator.validate(address_data)
        return await self.repository.update_address(address_data, address_id)

    async def delete_address(self, address_id: UUID) -> None:
        """Delete an address."""
        return await self.repository.delete_address(address_id)
