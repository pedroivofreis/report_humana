"""Role router."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.schemas.role import (
    AssignRoleByNameRequest,
    AssignRoleRequest,
    RoleCreateRequest,
    RoleResponse,
    RoleUpdateRequest,
    UserRoleResponse,
)
from app.api.services.role import RoleService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=list[RoleResponse], status_code=status.HTTP_200_OK)
async def get_roles(
    is_active: bool | None = Query(None, description="Filter by active status"),
    role_service: RoleService = Depends(),
) -> list[RoleResponse]:
    """Get all roles."""
    logger.info("GET /roles - Getting all roles")
    return await role_service.get_roles(is_active=is_active)


@router.get("/{role_id}", response_model=RoleResponse, status_code=status.HTTP_200_OK)
async def get_role_by_id(
    role_id: UUID,
    role_service: RoleService = Depends(),
) -> RoleResponse:
    """Get a role by ID."""
    logger.info(f"GET /roles/{role_id} - Getting role by ID")
    return await role_service.get_role_by_id(role_id)


@router.get("/name/{role_name}", response_model=RoleResponse, status_code=status.HTTP_200_OK)
async def get_role_by_name(
    role_name: str,
    role_service: RoleService = Depends(),
) -> RoleResponse:
    """Get a role by name."""
    logger.info(f"GET /roles/name/{role_name} - Getting role by name")
    return await role_service.get_role_by_name(role_name)


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreateRequest,
    role_service: RoleService = Depends(),
) -> RoleResponse:
    """Create a new role."""
    logger.info(f"POST /roles - Creating role: {role_data.name}")
    return await role_service.create_role(role_data)


@router.put("/{role_id}", response_model=RoleResponse, status_code=status.HTTP_200_OK)
async def update_role(
    role_id: UUID,
    role_data: RoleUpdateRequest,
    role_service: RoleService = Depends(),
) -> RoleResponse:
    """Update a role."""
    logger.info(f"PUT /roles/{role_id} - Updating role")
    return await role_service.update_role(role_id, role_data)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: UUID,
    role_service: RoleService = Depends(),
) -> None:
    """Delete a role."""
    logger.info(f"DELETE /roles/{role_id} - Deleting role")
    await role_service.delete_role(role_id)


# Management of user roles
@router.post(
    "/users/{user_id}/assign",
    response_model=UserRoleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def assign_role_to_user(
    user_id: UUID,
    role_request: AssignRoleRequest,
    role_service: RoleService = Depends(),
) -> UserRoleResponse:
    """Assign a role to a user."""
    logger.info(f"POST /roles/users/{user_id}/assign - Assigning role to user")
    return await role_service.assign_role_to_user(user_id, role_request)


@router.post(
    "/users/{user_id}/assign-by-name",
    response_model=UserRoleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def assign_role_to_user_by_name(
    user_id: UUID,
    role_request: AssignRoleByNameRequest,
    role_service: RoleService = Depends(),
) -> UserRoleResponse:
    """Assign a role to a user by role name."""
    logger.info(f"POST /roles/users/{user_id}/assign-by-name - Assigning role to user by name")
    return await role_service.assign_role_to_user_by_name(user_id, role_request)


@router.delete("/users/{user_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_role_from_user(
    user_id: UUID,
    role_id: UUID,
    role_service: RoleService = Depends(),
) -> None:
    """Remove a role from a user."""
    logger.info(f"DELETE /roles/users/{user_id}/roles/{role_id} - Removing role from user")
    await role_service.remove_role_from_user(user_id, role_id)


@router.get("/users/{user_id}", response_model=list[RoleResponse], status_code=status.HTTP_200_OK)
async def get_user_roles(
    user_id: UUID,
    role_service: RoleService = Depends(),
) -> list[RoleResponse]:
    """Get all roles for a user."""
    logger.info(f"GET /roles/users/{user_id} - Getting roles for user")
    return await role_service.get_user_roles(user_id)


@router.get("/{role_id}/users", response_model=list[UUID], status_code=status.HTTP_200_OK)
async def get_users_by_role(
    role_id: UUID,
    role_service: RoleService = Depends(),
) -> list[UUID]:
    """Get all user IDs with a specific role."""
    logger.info(f"GET /roles/{role_id}/users - Getting users with role")
    return await role_service.get_users_by_role(role_id)
