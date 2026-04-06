"""User service module."""

from uuid import UUID

import structlog
from fastapi import Depends, UploadFile

from app.api.models.user import UserStatus
from app.api.repositories.role import RoleRepository
from app.api.repositories.user import UserRepository
from app.api.schemas.user import (
    ChangePasswordRequest,
    UserCreateRequest,
    UserListResponse,
    UserResponse,
    UserResponseById,
    UserUpdateRequest,
)
from app.api.services.attachment import AttachmentService
from app.api.utils.s3 import s3_service
from app.api.validators.user import UserValidator
from app.core.exceptions import BadRequestException, NotFoundException
from app.core.security import get_password_hash, verify_password

logger = structlog.getLogger(__name__)


class UserService:
    """User service."""

    def __init__(
        self,
        repository: UserRepository = Depends(UserRepository),
        attachment_service: AttachmentService = Depends(AttachmentService),
        role_repository: RoleRepository = Depends(RoleRepository),
    ):
        self.repository = repository
        self.attachment_service = attachment_service
        self.role_repository = role_repository

    async def get_users(
        self,
        page: int = 1,
        page_size: int = 10,
        is_active: bool | None = None,
        name: str | None = None,
        status: UserStatus | None = None,
        role: list[str] | None = None,
    ) -> UserListResponse:
        """Get all users with pagination and filters."""
        logger.debug(
            f"Getting users with page={page}, page_size={page_size}, is_active={is_active}, "
            f"name={name}, status={status}, role={role}"
        )
        return await self.repository.get_users(
            page=page,
            page_size=page_size,
            is_active=is_active,
            name=name,
            status=status,
            role=role,
        )

    async def get_user_by_id(self, user_id: UUID) -> UserResponseById:
        """Get a user by id."""
        logger.debug(f"Getting user by id: {user_id}")
        user = await self.repository.get_user_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        attachments = await self.attachment_service.get_attachments_by_entity(user_id, "user")
        user.attachments = attachments

        return user

    async def get_user_by_cpf(self, cpf: str) -> UserResponse | None:
        """Get a user by cpf."""
        logger.debug(f"Getting user by cpf: {cpf}")
        return await self.repository.get_user_by_cpf(cpf)

    async def create_user(
        self, user: UserCreateRequest, file: UploadFile | None = None
    ) -> UserResponse:
        """Create a user with optional profile picture upload."""
        logger.debug("Creating user service")

        user = UserValidator().validate(user)

        if await self.repository.get_user_by_email(user.email):
            raise BadRequestException("Email ja cadastrado")

        if await self.repository.get_user_by_cpf(user.cpf):
            raise BadRequestException("CPF ja cadastrado")

        if user.phone and await self.repository.get_user_by_phone(user.phone):
            raise BadRequestException("Telefone ja cadastrado")

        if file and file.filename:
            profile_picture_url = await s3_service.upload_file(file, folder="profile-pictures")
            user.profile_picture = profile_picture_url

        return await self.repository.create_user(user)

    async def update_user(
        self, user_id: UUID, user: UserUpdateRequest, file: UploadFile | None = None
    ) -> UserResponse:
        """Update a user with optional profile picture upload."""
        logger.debug(f"Updating user id: {user_id}")

        current_user = await self.repository.get_user_by_id(user_id)
        if current_user is None:
            raise NotFoundException("User not found")

        if user.email:
            existing_user = await self.repository.get_user_by_email(user.email)
            if existing_user and existing_user.id != user_id:
                raise BadRequestException("Email ja cadastrado")

        if user.cpf:
            existing_user = await self.repository.get_user_by_cpf(user.cpf)
            if existing_user and existing_user.id != user_id:
                raise BadRequestException("CPF ja cadastrado")

        if user.phone:
            existing_user = await self.repository.get_user_by_phone(user.phone)
            if existing_user and existing_user.id != user_id:
                raise BadRequestException("Telefone ja cadastrado")

        if file:
            try:
                profile_picture_url = await s3_service.upload_file(file, folder="profile-pictures")
                user.profile_picture = profile_picture_url

                if current_user.profile_picture:
                    try:
                        s3_service.delete_file(current_user.profile_picture)
                    except Exception as e:
                        logger.warning(f"Failed to delete old profile picture from S3: {str(e)}")

            except Exception as e:
                logger.error(f"Failed to upload profile picture to S3: {str(e)}")
                raise BadRequestException(
                    f"Failed to upload profile picture to S3: {str(e)}"
                ) from e

        return await self.repository.update_user(user_id, user)

    async def delete_user(self, user_id: UUID) -> None:
        """Delete a user."""
        logger.debug(f"Deleting user id: {user_id}")

        current_user = await self.repository.get_user_by_id(user_id)
        if current_user is None:
            raise NotFoundException("User not found")

        if current_user.profile_picture:
            try:
                s3_service.delete_file(current_user.profile_picture)
            except Exception as e:
                logger.warning(f"Failed to delete profile picture from S3: {str(e)}")

        return await self.repository.delete_user(user_id)

    async def change_password(self, user_id: UUID, request: ChangePasswordRequest) -> None:
        """Change user password."""
        logger.debug(f"Changing password for user id: {user_id}")

        user = await self.repository.get_user_auth_data_by_email(
            (await self.get_user_by_id(user_id)).email
        )
        if not user:
            raise NotFoundException("User not found")

        if not user.password or not verify_password(request.old_password, user.password):
            raise BadRequestException("Incorrect old password")

        hashed_password = get_password_hash(request.new_password)
        await self.repository.update_password(user_id, hashed_password)
