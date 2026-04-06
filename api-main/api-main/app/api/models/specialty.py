"""Specialty model module."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid_utils import uuid7

from app.db.session import Base

if TYPE_CHECKING:
    from app.api.models.profession import Profession
    from app.api.models.user_specialty import UserSpecialty


class Specialty(Base):
    """Specialty model."""

    __tablename__ = "specialties"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid7)
    code: Mapped[str | None] = mapped_column(String(16), nullable=True, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=text("CURRENT_TIMESTAMP"), nullable=True
    )

    # Relationships
    user_specialties: Mapped[list[UserSpecialty]] = relationship(
        "UserSpecialty", back_populates="specialty"
    )

    def __repr__(self) -> str:
        return f"<Specialty(id={self.id}, name={self.name}, code={self.code}, is_active={self.is_active})>"
