"""User Observation model module."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Text, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid_utils import uuid7

from app.db.session import Base

if TYPE_CHECKING:
    from app.api.models.user import User


class UserObservation(Base):
    """User Observation model."""

    __tablename__ = "user_observations"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid7)
    target_user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    owner_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    observation: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )

    # Relationships
    target_user: Mapped["User"] = relationship(
        "User",
        foreign_keys="[UserObservation.target_user_id]",
        back_populates="received_observations",
    )
    owner: Mapped["User"] = relationship(
        "User",
        foreign_keys="[UserObservation.owner_id]",
        back_populates="made_observations",
    )

    def __repr__(self) -> str:
        return f"<UserObservation(id={self.id}, target_user_id={self.target_user_id}, owner_id={self.owner_id})>"
