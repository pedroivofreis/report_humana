"""Role schema module."""

from datetime import datetime
from enum import Enum
from uuid import UUID

import pydantic


class RoleEnum(str, Enum):
    """Enum kept for compatibility, but now roles are dynamic."""

    ADMIN = "admin"
    MANAGER = "manager"
    PROFESSIONAL = "professional"


class RoleResponse(pydantic.BaseModel):
    """Schema for Role response."""

    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None


class RoleCreateRequest(pydantic.BaseModel):
    """Schema for Role creation."""

    name: str = pydantic.Field(..., min_length=1, max_length=100, description="Role name")
    description: str | None = pydantic.Field(None, max_length=255, description="Role description")
    is_active: bool = pydantic.Field(True, description="If the role is active")


class RoleUpdateRequest(pydantic.BaseModel):
    """Schema for Role update."""

    name: str | None = pydantic.Field(None, min_length=1, max_length=100, description="Role name")
    description: str | None = pydantic.Field(None, max_length=255, description="Role description")
    is_active: bool | None = pydantic.Field(None, description="If the role is active")


class UserRoleResponse(pydantic.BaseModel):
    """Schema for UserRole response."""

    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    role_id: UUID
    created_at: datetime
    role: RoleResponse | None = None


class AssignRoleRequest(pydantic.BaseModel):
    """Schema for assigning a role to a user."""

    role_id: UUID = pydantic.Field(..., description="Role ID to be assigned")


class AssignRoleByNameRequest(pydantic.BaseModel):
    """Schema for assigning a role to a user by name."""

    role_name: str = pydantic.Field(..., description="Role name to be assigned")
