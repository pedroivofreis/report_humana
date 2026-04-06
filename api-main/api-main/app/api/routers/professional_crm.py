"""Professional CRM router module."""

from uuid import UUID

import fastapi
import structlog
from fastapi import Depends

from app.api.schemas.professional_crm import (
    ProfessionalCrmCreateRequest,
    ProfessionalCrmResponse,
    ProfessionalCrmUpdateRequest,
)
from app.api.services.professional_crm import ProfessionalCrmService

logger = structlog.get_logger(__name__)

router = fastapi.APIRouter()


@router.get(
    "",
    response_model=list[ProfessionalCrmResponse],
    status_code=200,
    description="Professional CRM endpoint to get all professional CRMs",
)
async def get_all_professional_crms(
    service: ProfessionalCrmService = Depends(ProfessionalCrmService),
) -> list[ProfessionalCrmResponse]:
    """
    Professional CRM endpoint to get all professional CRMs.

    Args:
        service: Professional CRM service dependency.

    Returns:
        list[ProfessionalCrmResponse]: List of professional CRMs.
    """
    logger.info("Getting all professional CRMs")
    return await service.get_all_professional_crms()


@router.get(
    "/{professional_crm_id}",
    response_model=ProfessionalCrmResponse,
    status_code=200,
    description="Professional CRM endpoint to get a professional CRM by id.",
)
async def get_professional_crm_by_id(
    professional_crm_id: UUID,
    service: ProfessionalCrmService = Depends(ProfessionalCrmService),
) -> ProfessionalCrmResponse:
    """
    Professional CRM endpoint to get a professional CRM by id.

    Args:
        professional_crm_id: Professional CRM id.
        service: Professional CRM service dependency.

    Returns:
        ProfessionalCrmResponse: Professional CRM.
    """
    logger.info("Getting professional CRM by id")
    logger.info(f"Professional CRM id: {professional_crm_id}")
    return await service.get_professional_crm_by_id(professional_crm_id)


@router.get(
    "/user/{user_id}",
    response_model=list[ProfessionalCrmResponse],
    status_code=200,
    description="Professional CRM endpoint to get all professional CRMs by user id.",
)
async def get_professional_crms_by_user_id(
    user_id: UUID,
    service: ProfessionalCrmService = Depends(ProfessionalCrmService),
) -> list[ProfessionalCrmResponse]:
    """
    Professional CRM endpoint to get all professional CRMs by user id.

    Args:
        user_id: User id.
        service: Professional CRM service dependency.

    Returns:
        list[ProfessionalCrmResponse]: List of professional CRMs for the user.
    """
    logger.info("Getting professional CRMs by user id")
    logger.info(f"User id: {user_id}")
    return await service.get_professional_crms_by_user_id(user_id)


@router.post(
    "",
    response_model=ProfessionalCrmResponse,
    status_code=201,
    description="Professional CRM endpoint to create a professional CRM.",
)
async def create_professional_crm(
    professional_crm: ProfessionalCrmCreateRequest,
    service: ProfessionalCrmService = Depends(ProfessionalCrmService),
) -> ProfessionalCrmResponse:
    """
    Professional CRM endpoint to create a professional CRM.

    Args:
        professional_crm: Professional CRM data.
        service: Professional CRM service dependency.

    Returns:
        ProfessionalCrmResponse: Professional CRM.
    """
    return await service.create_professional_crm(professional_crm)


@router.put(
    "/{professional_crm_id}",
    response_model=ProfessionalCrmResponse,
    status_code=200,
    description="Professional CRM endpoint to update a professional CRM.",
)
async def update_professional_crm(
    professional_crm_id: UUID,
    professional_crm: ProfessionalCrmUpdateRequest,
    service: ProfessionalCrmService = Depends(ProfessionalCrmService),
) -> ProfessionalCrmResponse:
    """
    Professional CRM endpoint to update a professional CRM.

    Args:
        professional_crm_id: Professional CRM id.
        professional_crm: Professional CRM data.
        service: Professional CRM service dependency.

    Returns:
        ProfessionalCrmResponse: Professional CRM.
    """
    logger.info("Updating professional CRM")
    logger.info(f"Professional CRM id: {professional_crm_id}")
    logger.info(f"Professional CRM: {professional_crm}")
    return await service.update_professional_crm(professional_crm_id, professional_crm)


@router.delete(
    "/{professional_crm_id}",
    status_code=204,
    description="Professional CRM endpoint to delete a professional CRM.",
)
async def delete_professional_crm(
    professional_crm_id: UUID,
    service: ProfessionalCrmService = Depends(ProfessionalCrmService),
) -> None:
    """
    Professional CRM endpoint to delete a professional CRM.

    Args:
        professional_crm_id: Professional CRM id.
        service: Professional CRM service dependency.

    Returns:
        None.
    """
    logger.info("Deleting professional CRM")
    logger.info(f"Professional CRM id: {professional_crm_id}")
    return await service.delete_professional_crm(professional_crm_id)
