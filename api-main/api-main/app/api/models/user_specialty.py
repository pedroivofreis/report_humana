"""User specialty model module."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, UniqueConstraint, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid_utils import uuid7

from app.db.session import Base

if TYPE_CHECKING:
    from app.api.models.specialty import Specialty
    from app.api.models.user import User


class UserSpecialty(Base):
    """User specialty model."""

    __tablename__ = "user_specialties"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid7)
    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    specialty_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("specialties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=text("CURRENT_TIMESTAMP"), nullable=True
    )

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="user_specialties")
    specialty: Mapped[Specialty] = relationship("Specialty", back_populates="user_specialties")

    # Unique constraint
    __table_args__ = (UniqueConstraint("user_id", "specialty_id", name="uq_user_specialty"),)

    def __repr__(self) -> str:
        return f"<UserSpecialty(id={self.id}, user_id={self.user_id}, specialty_id={self.specialty_id}, is_primary={self.is_primary})>"
