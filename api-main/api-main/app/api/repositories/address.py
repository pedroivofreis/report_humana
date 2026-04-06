"""Address repository."""

from uuid import UUID

import structlog
from fastapi import Depends
from sqlalchemy import select

from app.api.models.address import Address
from app.api.schemas.address import AddressCreateRequest, AddressResponse, AddressUpdateRequest
from app.core.exceptions import NotFoundException
from app.db.session import AsyncSession, get_db_session

logger = structlog.get_logger(__name__)


class AddressRepository:
    """Address repository."""

    def __init__(self, db: AsyncSession = Depends(get_db_session)):
        self.db = db

    async def get_addresses(self) -> list[AddressResponse]:
        """Get all addresses."""
        logger.debug("get_addresses called")
        result = await self.db.execute(select(Address))
        addresses = result.scalars().all()
        logger.debug(f"Retrieved {len(addresses)} addresses")

        return [AddressResponse.model_validate(address) for address in addresses]

    async def get_address_by_id(self, address_id: UUID) -> AddressResponse | None:
        """Get an address by id."""
        logger.debug(f"get_address_by_id called for address_id={address_id}")
        result = await self.db.execute(select(Address).where(Address.id == address_id))
        address = result.scalar_one_or_none()
        logger.debug(f"Address found: {address is not None}")

        if not address:
            raise NotFoundException("Address not found")

        return AddressResponse.model_validate(address)

    async def get_address_by_zip_code(self, zip_code: str) -> list[AddressResponse]:
        """Get addresses by zip code."""
        logger.debug(f"get_address_by_zip_code called for zip_code={zip_code}")
        result = await self.db.execute(select(Address).where(Address.zip_code == zip_code))
        addresses = result.scalars().all()
        logger.debug(f"Found {len(addresses)} addresses")

        return [AddressResponse.model_validate(address) for address in addresses]

    async def get_addresses_by_user_id(self, user_id: UUID) -> list[AddressResponse]:
        """Get addresses by user id."""
        logger.debug(f"get_addresses_by_user_id called for user_id={user_id}")
        result = await self.db.execute(select(Address).where(Address.user_id == user_id))
        addresses = result.scalars().all()
        logger.debug(f"Found {len(addresses)} addresses")

        return [AddressResponse.model_validate(address) for address in addresses]

    async def create_address(self, address: AddressCreateRequest) -> AddressResponse:
        """Create an address."""
        logger.debug("create_address called")

        address_data = address.model_dump()
        new_address = Address(**address_data)

        self.db.add(new_address)
        await self.db.commit()
        await self.db.refresh(new_address)

        return AddressResponse.model_validate(new_address)

    async def update_address(
        self, address_id: UUID, addressData: AddressUpdateRequest
    ) -> AddressResponse:
        """Update an address."""
        logger.debug(f"update_address called for address_id={address_id}")

        result = await self.db.execute(select(Address).where(Address.id == address_id))
        address = result.scalar_one_or_none()

        if not address:
            raise NotFoundException("Address not found")

        for key, value in addressData.model_dump(exclude_unset=True).items():
            setattr(address, key, value)

        await self.db.commit()
        await self.db.refresh(address)

        return AddressResponse.model_validate(address)

    async def delete_address(self, address_id: UUID) -> None:
        """Delete an address."""
        logger.debug(f"delete_address called for address_id={address_id}")
        result = await self.db.execute(select(Address).where(Address.id == address_id))
        address = result.scalar_one_or_none()

        if not address:
            raise NotFoundException("Address not found")

        await self.db.delete(address)
        await self.db.commit()
