from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.schemas.user_absence import UserAbsenceCreate, UserAbsenceResponse
from app.api.services.user_absence import UserAbsenceService

router = APIRouter(tags=["User Absences"])


@router.post(
    "",
    response_model=UserAbsenceResponse,
    status_code=201,
    description="User absence endpoint to create an absence.",
)
async def create_user_absence(
    absence_in: UserAbsenceCreate,
    service: UserAbsenceService = Depends(UserAbsenceService),
) -> UserAbsenceResponse:
    """
    User absence endpoint to create an absence.

    Args:
        absence_in: Absence data.
        service: User absence service dependency.

    Returns:
        UserAbsenceResponse: Created absence.
    """
    result = await service.create_absence(absence_in)
    return UserAbsenceResponse.model_validate(result)


@router.get(
    "/user/{user_id}",
    response_model=list[UserAbsenceResponse],
    status_code=200,
    description="User absence endpoint to get absences by user id.",
)
async def get_user_absences(
    user_id: UUID,
    service: UserAbsenceService = Depends(UserAbsenceService),
) -> list[UserAbsenceResponse]:
    """
    User absence endpoint to get absences by user id.

    Args:
        user_id: User id.
        service: User absence service dependency.

    Returns:
        list[UserAbsenceResponse]: List of user absences.
    """
    result = await service.get_user_absences(user_id)
    return [UserAbsenceResponse.model_validate(absence) for absence in result]


@router.get(
    "/sector/{sector_id}",
    response_model=list[UserAbsenceResponse],
    status_code=200,
    description="User absence endpoint to get absences by sector id.",
)
async def get_absences_by_sector(
    sector_id: UUID,
    service: UserAbsenceService = Depends(UserAbsenceService),
) -> list[UserAbsenceResponse]:
    """
    User absence endpoint to get absences by sector id.

    Args:
        sector_id: Sector id.
        service: User absence service dependency.

    Returns:
        list[UserAbsenceResponse]: List of user absences.
    """
    result = await service.get_absences_by_sector(sector_id)
    return [UserAbsenceResponse.model_validate(absence) for absence in result]
