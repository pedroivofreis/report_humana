"""Role model module."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid_utils import uuid7

from app.db.session import Base

if TYPE_CHECKING:
    from app.api.models.user_role import UserRole


class Role(Base):
    """Role model."""

    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid7)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=text("CURRENT_TIMESTAMP"), nullable=True
    )

    # Relationship with users_roles
    user_roles: Mapped[list[UserRole]] = relationship(
        "UserRole", back_populates="role", cascade="all, delete-orphan"
    )
