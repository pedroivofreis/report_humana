"""Attachment service module."""

from uuid import UUID

import structlog
from fastapi import Depends, UploadFile

from app.api.repositories.attachment import AttachmentRepository
from app.api.repositories.user import UserRepository
from app.api.schemas.attachment import (
    AttachmentCreateRequest,
    AttachmentResponse,
    AttachmentUpdateRequest,
)
from app.api.utils.s3 import s3_service
from app.core.exceptions import BadRequestException, NotFoundException

logger = structlog.getLogger(__name__)


class AttachmentService:
    """Attachment service."""

    def __init__(
        self,
        repository: AttachmentRepository = Depends(AttachmentRepository),
        user_repository: UserRepository = Depends(UserRepository),
    ):
        self.repository = repository
        self.user_repository = user_repository

    async def get_attachments(self) -> list[AttachmentResponse]:
        """Get all attachments."""
        logger.debug("Getting all attachments")
        return await self.repository.get_attachments()

    async def get_attachments_by_entity(self, entity_id: UUID, entity_type: str) -> list[AttachmentResponse]:
        """Get attachments by entity."""
        logger.debug(f"Getting attachments by entity: {entity_type} {entity_id}")
        return await self.repository.get_attachments_by_entity(entity_id, entity_type)

    async def get_attachment_by_id(self, attachment_id: UUID) -> AttachmentResponse | None:
        """Get an attachment by id."""
        logger.debug(f"Getting attachment by id: {attachment_id}")
        attachment = await self.repository.get_attachment_by_id(attachment_id)
        if not attachment:
            raise NotFoundException("Attachment not found")

        return attachment

    async def create_attachment(
        self,
        attachment: AttachmentCreateRequest,
        file: UploadFile | None = None,
    ) -> AttachmentResponse:
        """Create an attachment (optional file upload)."""
        logger.debug("Creating attachment service")

        file_url: str | None = None
        file_key: str | None = None

        if file:
            try:
                file_url, file_key = await s3_service.upload_file_return_key(file, folder="attachments")
            except Exception as e:
                logger.error(f"Failed to upload file to S3: {str(e)}")
                raise BadRequestException(f"Failed to upload file to S3: {str(e)}") from e

        return await self.repository.create_attachment(attachment, file_url, file_key)

    async def update_attachment(
        self,
        attachment_id: UUID,
        attachment: AttachmentUpdateRequest,
        file: UploadFile | None = None,
    ) -> AttachmentResponse:
        """Update an attachment."""
        logger.debug(f"Updating attachment id: {attachment_id}")

        current_attachment = await self.repository.get_attachment_by_id(attachment_id)
        if not current_attachment:
            raise NotFoundException("Attachment not found")

        file_url = None
        file_key = None

        if file:
            try:
                file_url, file_key = await s3_service.upload_file_return_key(file, folder="attachments")

                if current_attachment.file_key:
                    try:
                        s3_service.delete_file_by_key(current_attachment.file_key)
                    except Exception as e:
                        logger.warning(f"Failed to delete old file from S3 key: {str(e)}")
                elif current_attachment.url:
                    try:
                        s3_service.delete_file(current_attachment.url)
                    except Exception as e:
                        logger.warning(f"Failed to delete old file from S3: {str(e)}")

            except Exception as e:
                logger.error(f"Failed to upload file to S3: {str(e)}")
                raise BadRequestException(f"Failed to upload file to S3: {str(e)}") from e

        return await self.repository.update_attachment(attachment_id, attachment, file_url, file_key)

    async def delete_attachment(self, attachment_id: UUID) -> None:
        """Delete an attachment."""
        logger.debug(f"Deleting attachment id: {attachment_id}")

        current_attachment = await self.repository.get_attachment_by_id(attachment_id)
        if not current_attachment:
            raise NotFoundException("Attachment not found")

        if current_attachment.file_key:
            try:
                s3_service.delete_file_by_key(current_attachment.file_key)
            except Exception as e:
                logger.warning(f"Failed to delete file from S3 key: {str(e)}")
        elif current_attachment.url:
            try:
                s3_service.delete_file(current_attachment.url)
            except Exception as e:
                logger.warning(f"Failed to delete file from S3: {str(e)}")

        return await self.repository.delete_attachment(attachment_id)
