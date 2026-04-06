"""Address service module."""

from uuid import UUID

import structlog
from fastapi import Depends

from app.api.repositories.address import AddressRepository
from app.api.schemas.address import AddressCreateRequest, AddressResponse, AddressUpdateRequest
from app.core.exceptions import NotFoundException

logger = structlog.getLogger(__name__)


class AddressService:
    """Address service."""

    def __init__(self, repository: AddressRepository = Depends(AddressRepository)):
        self.repository = repository

    async def get_addresses(self) -> list[AddressResponse]:
        """Get all addresses."""
        logger.debug("Get all addresses")
        return await self.repository.get_addresses()

    async def get_addresses_by_user_id(self, user_id: UUID) -> list[AddressResponse]:
        """Get addresses by user id."""
        logger.debug(f"Get addresses by user id: {user_id}")
        return await self.repository.get_addresses_by_user_id(user_id)

    async def get_address_by_id(self, address_id: UUID) -> AddressResponse | None:
        """Get an address by id."""
        logger.debug(f"Get address by id: {address_id}")
        address = await self.repository.get_address_by_id(address_id)
        if not address:
            raise NotFoundException("Address not found")

        return address

    async def create_address(self, address: AddressCreateRequest) -> AddressResponse:
        """Create an address."""
        logger.debug("Create address service")
        return await self.repository.create_address(address)

    async def update_address(
        self, address_id: UUID, address: AddressUpdateRequest
    ) -> AddressResponse:
        """Update an address."""
        logger.debug(f"Update address by id: {address_id}")

        if await self.repository.get_address_by_id(address_id) is None:
            raise NotFoundException("Address not found")

        return await self.repository.update_address(address_id, address)

    async def delete_address(self, address_id: UUID) -> None:
        """Delete an address."""
        logger.debug(f"Delete address by id: {address_id}")

        if await self.repository.get_address_by_id(address_id) is None:
            raise NotFoundException("Address not found")

        return await self.repository.delete_address(address_id)
