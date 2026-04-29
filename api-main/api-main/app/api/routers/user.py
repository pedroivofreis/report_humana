"""User router module."""

from uuid import UUID

import fastapi
import structlog
from fastapi import Depends

from app.api.dependencies.authentication import get_current_user, CreateUserRoleChecker, UpdateUserRoleChecker
from app.api.models.user import UserStatus
from app.api.schemas.user import (
    ChangePasswordRequest,
    UserCreateRequestForm,
    UserListResponse,
    UserRegisterStatusResponse,
    UserResponse,
    UserResponseById,
    UserUpdateRequest,
    UserUpdateRequestForm,
)
from app.api.services.user import UserService

logger = structlog.get_logger(__name__)

router = fastapi.APIRouter()


@router.get(
    "",
    response_model=UserListResponse,
    status_code=200,
    description="User endpoint with pagination and filters",
)
async def user(
    page: int = 1,
    page_size: int = 10,
    is_active: bool | None = None,
    name: str | None = None,
    status: UserStatus | None = None,
    role: list[str] = fastapi.Query(["professional"], alias="role[]", description="Filter by user roles"),
    service: UserService = Depends(UserService),
) -> UserListResponse:
    """
    User endpoint to get all users with pagination and filters.

    Args:
        page: Page number (default: 1).
        page_size: Number of items per page (default: 10).
        is_active: Filter by user status (active/inactive).
        name: Filter by first name or last name (partial match).
        status: Filter by user status (REGISTERED, ACTIVE, INACTIVE, etc.).
        role: Filter by user roles (professional, admin, manager).
        service: User service dependency.

    Returns:
        UserListResponse: Paginated list of users.
    """
    logger.info(
        f"Getting users - page: {page}, page_size: {page_size}, is_active: {is_active}, "
        f"name: {name}, status: {status}, role: {role}"
    )
    return await service.get_users(
        page=page,
        page_size=page_size,
        is_active=is_active,
        name=name,
        status=status,
        role=role,
    )


@router.get(
    "/{user_id}",
    response_model=UserResponseById,
    status_code=200,
    description="User endpoint to get a user by id.",
)
async def user_by_id(
    user_id: UUID,
    service: UserService = Depends(UserService),
) -> UserResponseById:
    """
    User endpoint to get a user by id.

    Args:
        user_id: User id.
        service: User service dependency.

    Returns:
        UserResponseById: User.
    """
    logger.info("Getting user by id")
    logger.info(f"User id: {user_id}")
    logger.info(f"Service: {service}")
    return await service.get_user_by_id(user_id)


@router.get(
    "/is-registered/{cpf}",
    response_model=UserRegisterStatusResponse | None,
    status_code=200,
    description="Check if a user is registered by CPF.",
)
async def check_user_registered(
    cpf: str,
    service: UserService = Depends(UserService),
) -> UserRegisterStatusResponse | None:
    """
    Check if a user is registered by CPF.

    Args:
        cpf: User CPF.
        service: User service dependency.

    Returns:
        UserRegisterStatusResponse or None.
    """
    logger.info("Checking if user is registered by cpf")
    user = await service.get_user_by_cpf(cpf)
    if not user:
        return None
    return UserRegisterStatusResponse(
        user_id=user.id,
        status=user.status,
        is_active=user.is_active,
    )


@router.post(
    "",
    response_model=UserResponse,
    status_code=201,
    description="User endpoint to create a user with optional profile picture upload.",
    dependencies=[Depends(CreateUserRoleChecker())]
)
async def create_user(
    user_data: UserCreateRequestForm = Depends(UserCreateRequestForm.as_form),
    service: UserService = Depends(UserService),
) -> UserResponse:
    """
    User endpoint to create a user with optional profile picture upload.

    Args:
        user_data: User data with optional profile picture file.
        service: User service dependency.

    Returns:
        UserResponse: User.
    """
    logger.info("Creating user")
    return await service.create_user(user_data, user_data.profile_picture_file)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=200,
    description="User endpoint to update a user with optional profile picture upload.",
    dependencies=[Depends(UpdateUserRoleChecker())]
)
async def update_user(
    user_id: UUID,
    user_data: UserUpdateRequestForm = Depends(UserUpdateRequestForm.as_form),
    service: UserService = Depends(UserService),
) -> UserResponse:
    """
    User endpoint to update a user with optional profile picture upload.

    Args:
        user_data: User data with optional profile picture file.
        service: User service dependency.

    Returns:
        UserResponse: User.
    """
    logger.info("Updating user")
    return await service.update_user(user_id, user_data, user_data.profile_picture_file)


@router.delete(
    "/{user_id}",
    status_code=204,
    description="User endpoint to delete a user.",
)
async def delete_user(
    user_id: UUID,
    service: UserService = Depends(UserService),
) -> None:
    """
    User endpoint to delete a user.

    Args:
        user_id: User id.
        service: User service dependency.

    Returns:
        None.
    """
    logger.info("Deleting user")
    logger.info(f"User id: {user_id}")
    logger.info(f"Service: {service}")
    return await service.delete_user(user_id)


@router.post(
    "/change-password",
    status_code=200,
    description="User endpoint to change password.",
)
async def change_password(
    request: ChangePasswordRequest,
    current_user: UserResponse = Depends(get_current_user),
    service: UserService = Depends(UserService),
) -> None:
    """
    User endpoint to change password.

    Args:
        request: Change password data.
        current_user: Authenticated user.
        service: User service dependency.

    Returns:
        None.
    """
    await service.change_password(current_user.id, request)


@router.put(
    "/me/profile-image",
    response_model=UserResponse,
    status_code=200,
    description="User endpoint to update the logged user's profile image.",
)
async def update_profile_image(
    formfile: fastapi.UploadFile = fastapi.File(...),
    current_user: UserResponse = Depends(get_current_user),
    service: UserService = Depends(UserService),
) -> UserResponse:
    """
    User endpoint to update profile image.

    Args:
        formfile: Profile image file.
        current_user: Authenticated user.
        service: User service dependency.

    Returns:
        UserResponse: Updated user.
    """
    logger.info("Updating user profile image")
    update_req = UserUpdateRequest(profile_picture="")
    return await service.update_user(current_user.id, update_req, formfile)
