"""Role repository."""

from uuid import UUID

import structlog
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.models.role import Role
from app.api.models.user_role import UserRole
from app.api.schemas.role import (
    AssignRoleRequest,
    RoleCreateRequest,
    RoleResponse,
    RoleUpdateRequest,
    UserRoleResponse,
)
from app.db.session import AsyncSession, get_db_session

logger = structlog.getLogger(__name__)


class RoleRepository:
    """Role repository."""

    def __init__(self, db: AsyncSession = Depends(get_db_session)):
        self.db = db

    async def get_roles(self, is_active: bool | None = None) -> list[RoleResponse]:
        """Get all roles."""
        logger.debug(f"get_roles called with is_active={is_active}")
        query = select(Role)

        if is_active is not None:
            query = query.where(Role.is_active == is_active)

        result = await self.db.execute(query)
        roles = result.scalars().all()

        return [RoleResponse.model_validate(role) for role in roles]

    async def get_role_by_id(self, role_id: UUID) -> RoleResponse | None:
        """Get a role by id."""
        logger.debug(f"get_role_by_id called for role_id={role_id}")
        result = await self.db.execute(select(Role).where(Role.id == role_id))
        role = result.scalar_one_or_none()
        return RoleResponse.model_validate(role) if role else None

    async def get_role_by_name(self, name: str) -> RoleResponse | None:
        """Get a role by name."""
        logger.debug(f"get_role_by_name called for name={name}")
        result = await self.db.execute(select(Role).where(Role.name == name))
        role = result.scalar_one_or_none()
        return RoleResponse.model_validate(role) if role else None

    async def create_role(self, role_data: RoleCreateRequest) -> RoleResponse:
        """Create a role."""
        logger.debug(f"create_role called for {role_data.name}")

        new_role = Role(**role_data.model_dump())
        self.db.add(new_role)
        await self.db.commit()
        await self.db.refresh(new_role)

        logger.debug(f"Role created with id: {new_role.id}")
        return RoleResponse.model_validate(new_role)

    async def update_role(self, role_id: UUID, role_data: RoleUpdateRequest) -> RoleResponse | None:
        """Update a role."""
        logger.debug(f"update_role called for role_id={role_id}")

        result = await self.db.execute(select(Role).where(Role.id == role_id))
        role = result.scalar_one_or_none()

        if not role:
            logger.warning(f"Role not found: {role_id}")
            return None

        for key, value in role_data.model_dump(exclude_unset=True).items():
            setattr(role, key, value)

        await self.db.commit()
        await self.db.refresh(role)

        logger.debug(f"Role updated: {role_id}")
        return RoleResponse.model_validate(role)

    async def delete_role(self, role_id: UUID) -> bool:
        """Delete a role."""
        logger.debug(f"delete_role called for role_id={role_id}")

        result = await self.db.execute(select(Role).where(Role.id == role_id))
        role = result.scalar_one_or_none()

        if not role:
            logger.warning(f"Role not found: {role_id}")
            return False

        await self.db.delete(role)
        await self.db.commit()

        logger.debug(f"Role deleted: {role_id}")
        return True

    async def assign_role_to_user(
        self, user_id: UUID, role_request: AssignRoleRequest
    ) -> UserRoleResponse:
        """Assign a role to a user."""
        logger.debug(
            f"assign_role_to_user called: role_id={role_request.role_id}, user_id={user_id}"
        )

        # Check if the role already exists
        result = await self.db.execute(
            select(UserRole).where(
                UserRole.user_id == user_id, UserRole.role_id == role_request.role_id
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            logger.warning("User role already exists")
            return UserRoleResponse.model_validate(existing)

        # Create new role
        user_role = UserRole(user_id=user_id, role_id=role_request.role_id)
        self.db.add(user_role)
        await self.db.commit()
        await self.db.refresh(user_role)

        logger.debug(f"Role assigned with id: {user_role.id}")
        return UserRoleResponse.model_validate(user_role)

    async def remove_role_from_user(self, user_id: UUID, role_id: UUID) -> bool:
        """Remove a role from a user."""
        logger.debug(f"remove_role_from_user called: role_id={role_id}, user_id={user_id}")

        result = await self.db.execute(
            select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id)
        )
        user_role = result.scalar_one_or_none()

        if not user_role:
            logger.warning("User role not found")
            return False

        await self.db.delete(user_role)
        await self.db.commit()

        logger.debug("Role removed from user")
        return True

    async def get_user_roles(self, user_id: UUID) -> list[RoleResponse]:
        """Get all roles for a user."""
        logger.debug(f"get_user_roles called for user_id={user_id}")

        result = await self.db.execute(
            select(Role)
            .join(UserRole)
            .where(UserRole.user_id == user_id)
            .options(selectinload(Role.user_roles))
        )
        roles = result.scalars().all()

        logger.debug(f"Found {len(roles)} roles for user")
        return [RoleResponse.model_validate(role) for role in roles]

    async def get_users_by_role(self, role_id: UUID) -> list[UUID]:
        """Get all user IDs with a specific role."""
        logger.debug(f"get_users_by_role called for role_id={role_id}")

        result = await self.db.execute(select(UserRole.user_id).where(UserRole.role_id == role_id))
        user_ids = result.scalars().all()

        logger.debug(f"Found {len(user_ids)} users with role")
        return list(user_ids)
