"""Attachment model module."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from uuid_utils import uuid7

from app.db.session import Base

if TYPE_CHECKING:
    from app.api.models.user import User


class Attachment(Base):
    """Attachment model."""

    __tablename__ = "attachments"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid7)
    entity_id: Mapped[UUID] = mapped_column(Uuid, nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(length=50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(length=255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    url: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    file_key: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
