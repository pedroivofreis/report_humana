"""Attachment repository."""

from uuid import UUID

import structlog
from fastapi import Depends
from sqlalchemy import select

from app.api.models.attachment import Attachment
from app.api.schemas.attachment import (
    AttachmentCreateRequest,
    AttachmentResponse,
    AttachmentUpdateRequest,
)
from app.core.exceptions import NotFoundException
from app.db.session import AsyncSession, get_db_session

logger = structlog.get_logger(__name__)


class AttachmentRepository:
    """Attachment repository."""

    def __init__(self, db: AsyncSession = Depends(get_db_session)):
        self.db = db

    async def get_attachments(self) -> list[AttachmentResponse]:
        """Get all attachments."""
        logger.debug("get_attachments called")
        result = await self.db.execute(select(Attachment))
        attachments = result.scalars().all()
        logger.debug(f"Retrieved {len(attachments)} attachments")

        return [AttachmentResponse.model_validate(attachment) for attachment in attachments]

    async def get_attachment_by_id(self, attachment_id: UUID) -> AttachmentResponse | None:
        """Get an attachment by id."""
        logger.debug(f"get_attachment_by_id called for attachment_id={attachment_id}")
        result = await self.db.execute(select(Attachment).where(Attachment.id == attachment_id))
        attachment = result.scalar_one_or_none()
        logger.debug(f"Attachment found: {attachment is not None}")

        if not attachment:
            raise NotFoundException("Attachment not found")

        return AttachmentResponse.model_validate(attachment)

    async def get_attachments_by_entity(self, entity_id: UUID, entity_type: str) -> list[AttachmentResponse]:
        """Get attachments by entity."""
        logger.debug(f"get_attachments_by_entity called for entity_id={entity_id}, entity_type={entity_type}")
        result = await self.db.execute(
            select(Attachment).where(
                (Attachment.entity_id == entity_id) & (Attachment.entity_type == entity_type)
            )
        )
        attachments = result.scalars().all()
        logger.debug(f"Found {len(attachments)} attachments")

        return [AttachmentResponse.model_validate(attachment) for attachment in attachments]

    async def create_attachment(
        self, attachment: AttachmentCreateRequest, file_url: str | None = None, file_key: str | None = None
    ) -> AttachmentResponse:
        """Create an attachment."""
        logger.debug("create_attachment called")

        attachment_data = attachment.model_dump(exclude={"file"}, exclude_none=True)
        if file_url:
            attachment_data["url"] = file_url
        if file_key:
            attachment_data["file_key"] = file_key
        new_attachment = Attachment(**attachment_data)

        self.db.add(new_attachment)
        await self.db.commit()
        await self.db.refresh(new_attachment)

        return AttachmentResponse.model_validate(new_attachment)

    async def update_attachment(
        self,
        attachment_id: UUID,
        attachmentData: AttachmentUpdateRequest,
        file_url: str | None = None,
        file_key: str | None = None,
    ) -> AttachmentResponse:
        """Update an attachment."""
        logger.debug(f"update_attachment called for attachment_id={attachment_id}")

        result = await self.db.execute(select(Attachment).where(Attachment.id == attachment_id))
        attachment = result.scalar_one_or_none()

        if not attachment:
            raise NotFoundException("Attachment not found")

        for key, value in attachmentData.model_dump(exclude_unset=True).items():
            setattr(attachment, key, value)

        if file_url:
            attachment.url = file_url
        if file_key:
            attachment.file_key = file_key

        await self.db.commit()
        await self.db.refresh(attachment)

        return AttachmentResponse.model_validate(attachment)

    async def delete_attachment(self, attachment_id: UUID) -> None:
        """Delete an attachment."""
        logger.debug(f"delete_attachment called for attachment_id={attachment_id}")
        result = await self.db.execute(select(Attachment).where(Attachment.id == attachment_id))
        attachment = result.scalar_one_or_none()

        if not attachment:
            raise NotFoundException("Attachment not found")

        await self.db.delete(attachment)
        await self.db.commit()
