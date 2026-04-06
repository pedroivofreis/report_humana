"""Role service."""

from uuid import UUID

import structlog
from fastapi import Depends

from app.api.repositories.role import RoleRepository
from app.api.schemas.role import (
    AssignRoleByNameRequest,
    AssignRoleRequest,
    RoleCreateRequest,
    RoleResponse,
    RoleUpdateRequest,
    UserRoleResponse,
)
from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
    ResourceAlreadyExistsException,
)

logger = structlog.getLogger(__name__)


class RoleService:
    """Role service."""

    def __init__(self, role_repository: RoleRepository = Depends()):
        self.role_repository = role_repository

    async def get_roles(self, is_active: bool | None = None) -> list[RoleResponse]:
        """Get all roles."""
        logger.debug(f"get_roles called with is_active={is_active}")
        return await self.role_repository.get_roles(is_active=is_active)

    async def get_role_by_id(self, role_id: UUID) -> RoleResponse:
        """Get a role by id."""
        logger.debug(f"get_role_by_id called for role_id={role_id}")
        role = await self.role_repository.get_role_by_id(role_id)

        if not role:
            raise NotFoundException("Role não encontrado")

        return role

    async def get_role_by_name(self, name: str) -> RoleResponse:
        """Get a role by name."""
        logger.debug(f"get_role_by_name called for name={name}")
        role = await self.role_repository.get_role_by_name(name)

        if not role:
            raise NotFoundException("Role não encontrado")

        return role

    async def create_role(self, role_data: RoleCreateRequest) -> RoleResponse:
        """Create a role."""
        logger.debug(f"create_role called for {role_data.name}")

        existing_role = await self.role_repository.get_role_by_name(role_data.name)

        if existing_role:
            raise ResourceAlreadyExistsException("Role com este nome já existe")

        return await self.role_repository.create_role(role_data)

    async def update_role(self, role_id: UUID, role_data: RoleUpdateRequest) -> RoleResponse:
        """Update a role."""
        logger.debug(f"update_role called for role_id={role_id}")

        if role_data.name:
            existing_role = await self.role_repository.get_role_by_name(role_data.name)

            if existing_role and existing_role.id != role_id:
                raise BadRequestException("Role com este nome já existe")

        role = await self.role_repository.update_role(role_id, role_data)

        if not role:
            raise NotFoundException("Role não encontrado")

        return role

    async def delete_role(self, role_id: UUID) -> None:
        """Delete a role."""
        logger.debug(f"delete_role called for role_id={role_id}")

        users_with_role = await self.role_repository.get_users_by_role(role_id)
        if users_with_role:
            raise BadRequestException(
                f"Cannot delete role: {len(users_with_role)} users have this role"
            )

        success = await self.role_repository.delete_role(role_id)

        if not success:
            raise NotFoundException("Role não encontrado")

    async def assign_role_to_user(
        self, user_id: UUID, role_request: AssignRoleRequest
    ) -> UserRoleResponse:
        """Assign a role to a user."""
        logger.debug(
            f"assign_role_to_user called: role_id={role_request.role_id}, user_id={user_id}"
        )

        await self.get_role_by_id(role_request.role_id)

        return await self.role_repository.assign_role_to_user(user_id, role_request)

    async def assign_role_to_user_by_name(
        self, user_id: UUID, role_request: AssignRoleByNameRequest
    ) -> UserRoleResponse:
        """Assign a role to a user by role name."""
        logger.debug(
            f"assign_role_to_user_by_name called: role_name={role_request.role_name}, user_id={user_id}"
        )

        role = await self.get_role_by_name(role_request.role_name)

        assign_request = AssignRoleRequest(role_id=role.id)
        return await self.role_repository.assign_role_to_user(user_id, assign_request)

    async def remove_role_from_user(self, user_id: UUID, role_id: UUID) -> None:
        """Remove a role from a user."""
        logger.debug(f"remove_role_from_user called: role_id={role_id}, user_id={user_id}")

        success = await self.role_repository.remove_role_from_user(user_id, role_id)

        if not success:
            raise NotFoundException("User role not found")

    async def get_user_roles(self, user_id: UUID) -> list[RoleResponse]:
        """Get all roles for a user."""
        logger.debug(f"get_user_roles called for user_id={user_id}")
        return await self.role_repository.get_user_roles(user_id)

    async def get_users_by_role(self, role_id: UUID) -> list[UUID]:
        """Get all user IDs with a specific role."""
        logger.debug(f"get_users_by_role called for role_id={role_id}")

        await self.get_role_by_id(role_id)

        return await self.role_repository.get_users_by_role(role_id)
