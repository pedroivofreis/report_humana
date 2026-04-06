"""Address router module."""

from uuid import UUID

import fastapi
import structlog
from fastapi import Depends, Query

from app.api.schemas.address import AddressCreateRequest, AddressResponse, AddressUpdateRequest
from app.api.services.addresses import AddressService

logger = structlog.get_logger(__name__)

router = fastapi.APIRouter()


@router.get(
    "",
    response_model=list[AddressResponse],
    status_code=200,
    description="Get all addresses",
)
async def get_addresses(
    service: AddressService = Depends(),
    include_deleted: bool = Query(
        default=False, description="Include deleted addresses", alias="include_deleted"
    ),
) -> list[AddressResponse]:
    """Get all addresses."""
    logger.debug("Getting all addresses", service=service)
    return await service.get_addresses(include_deleted)


@router.get(
    "/{address_id}",
    response_model=AddressResponse,
    status_code=200,
    description="Get address by ID",
)
async def get_address(
    address_id: UUID,
    service: AddressService = Depends(),
    include_deleted: bool = Query(
        default=False, description="Include deleted addresses", alias="include_deleted"
    ),
) -> AddressResponse:
    """Get address by ID."""
    logger.debug("Getting address by id", address_id=str(address_id))
    return await service.get_address_by_id(address_id, include_deleted)


@router.post(
    "",
    response_model=AddressResponse,
    status_code=201,
    description="Create an address",
)
async def create_address(
    address: AddressCreateRequest,
    service: AddressService = Depends(),
) -> AddressResponse:
    """Create an address."""
    logger.debug("Creating address", address=address)
    return await service.create_address(address)


@router.put(
    "/{address_id}",
    response_model=AddressResponse,
    status_code=200,
    description="Update an address",
)
async def update_address(
    address_id: UUID,
    address: AddressUpdateRequest,
    service: AddressService = Depends(),
) -> AddressResponse:
    """Update an address."""
    logger.debug("Updating address", address_id=str(address_id), address=address)
    return await service.update_address(address_id, address)


@router.delete(
    "/{address_id}",
    status_code=204,
    description="Delete an address",
)
async def delete_address(
    address_id: UUID,
    service: AddressService = Depends(),
) -> None:
    """Delete an address."""
    logger.debug("Deleting address", address_id=str(address_id))
    return await service.delete_address(address_id)
