"""Address router module."""

from uuid import UUID

import fastapi
import structlog
from fastapi import Depends

from app.api.schemas.address import AddressCreateRequest, AddressResponse, AddressUpdateRequest
from app.api.services.address import AddressService

logger = structlog.get_logger(__name__)

router = fastapi.APIRouter()


@router.get(
    "",
    response_model=list[AddressResponse],
    status_code=200,
    description="Address endpoint to get all addresses",
)
async def addresses(
    service: AddressService = Depends(AddressService),
) -> list[AddressResponse]:
    """
    Address endpoint to get all addresses.

    Args:
        service: Address service dependency.

    Returns:
        list[AddressResponse]: List of addresses.
    """
    logger.info("Getting all addresses")
    logger.info(f"Service: {service}")
    return await service.get_addresses()


@router.get(
    "/{address_id}",
    response_model=AddressResponse,
    status_code=200,
    description="Address endpoint to get an address by id.",
)
async def address_by_id(
    address_id: UUID,
    service: AddressService = Depends(AddressService),
) -> AddressResponse | None:
    """
    Address endpoint to get an address by id.

    Args:
        address_id: Address id.
        service: Address service dependency.

    Returns:
        AddressResponse: Address.
    """
    logger.info("Getting address by id")
    logger.info(f"Address id: {address_id}")
    logger.info(f"Service: {service}")
    return await service.get_address_by_id(address_id)


@router.post(
    "",
    response_model=AddressResponse,
    status_code=201,
    description="Address endpoint to create an address.",
)
async def create_address(
    address: AddressCreateRequest,
    service: AddressService = Depends(AddressService),
) -> AddressResponse:
    """
    Address endpoint to create an address.

    Args:
        address: Address data.
        service: Address service dependency.

    Returns:
        AddressResponse: Address.
    """
    logger.info("Creating address")
    logger.info(f"Address: {address}")
    logger.info(f"Service: {service}")
    return await service.create_address(address)


@router.put(
    "/{address_id}",
    response_model=AddressResponse,
    status_code=200,
    description="Address endpoint to update an address.",
)
async def update_address(
    address_id: UUID,
    address: AddressUpdateRequest,
    service: AddressService = Depends(AddressService),
) -> AddressResponse:
    """
    Address endpoint to update an address.

    Args:
        address_id: Address id.
        address: Address data.
        service: Address service dependency.

    Returns:
        AddressResponse: Address.
    """
    logger.info("Updating address")
    logger.info(f"Address id: {address_id}")
    logger.info(f"Address: {address}")
    logger.info(f"Service: {service}")
    return await service.update_address(address_id, address)


@router.delete(
    "/{address_id}",
    status_code=204,
    description="Address endpoint to delete an address.",
)
async def delete_address(
    address_id: UUID,
    service: AddressService = Depends(AddressService),
) -> None:
    """
    Address endpoint to delete an address.

    Args:
        address_id: Address id.
        service: Address service dependency.

    Returns:
        None.
    """
    logger.info("Deleting address")
    logger.info(f"Address id: {address_id}")
    logger.info(f"Service: {service}")
    return await service.delete_address(address_id)
