"""Attachment router module."""

from uuid import UUID

import fastapi
import structlog
from fastapi import Depends, File, Form, UploadFile

from app.api.schemas.attachment import (
    AttachmentCreateRequestForm,
    AttachmentResponse,
    AttachmentUpdateRequest,
)
from app.api.services.attachment import AttachmentService

logger = structlog.get_logger(__name__)

router = fastapi.APIRouter()


@router.get(
    "",
    response_model=list[AttachmentResponse],
    status_code=200,
    description="Attachment endpoint to get all attachments",
)
async def attachments(
    service: AttachmentService = Depends(AttachmentService),
) -> list[AttachmentResponse]:
    """
    Attachment endpoint to get all attachments.

    Args:
        service: Attachment service dependency.

    Returns:
        list[AttachmentResponse]: List of attachments.
    """
    logger.info("Getting all attachments")
    logger.info(f"Service: {service}")
    return await service.get_attachments()


@router.get(
    "/{attachment_id}",
    response_model=AttachmentResponse,
    status_code=200,
    description="Attachment endpoint to get an attachment by id.",
)
async def attachment_by_id(
    attachment_id: UUID,
    service: AttachmentService = Depends(AttachmentService),
) -> AttachmentResponse | None:
    """
    Attachment endpoint to get an attachment by id.

    Args:
        attachment_id: Attachment id.
        service: Attachment service dependency.

    Returns:
        AttachmentResponse: Attachment.
    """
    logger.info("Getting attachment by id")
    logger.info(f"Attachment id: {attachment_id}")
    logger.info(f"Service: {service}")
    return await service.get_attachment_by_id(attachment_id)


@router.get(
    "/{entity_type}/{entity_id}",
    response_model=list[AttachmentResponse],
    status_code=200,
    description="Attachment endpoint to get attachments by entity id and type.",
)
async def attachments_by_entity(
    entity_id: UUID,
    entity_type: str,
    service: AttachmentService = Depends(AttachmentService),
) -> list[AttachmentResponse]:
    """
    Attachment endpoint to get attachments by entity id and type.

    Args:
        entity_id: Entity id.
        entity_type: Entity type.
        service: Attachment service dependency.

    Returns:
        list[AttachmentResponse]: List of attachments.
    """
    logger.info("Getting attachments by entity")
    logger.info(f"Entity: {entity_type} {entity_id}")
    logger.info(f"Service: {service}")
    return await service.get_attachments_by_entity(entity_id, entity_type)


@router.post(
    "",
    response_model=AttachmentResponse,
    status_code=201,
    description="Attachment endpoint to create an attachment with file upload.",
)
async def create_attachment(
    attachment_data: AttachmentCreateRequestForm = Depends(AttachmentCreateRequestForm.as_form),
    service: AttachmentService = Depends(AttachmentService),
) -> AttachmentResponse:
    """
    Attachment endpoint to create an attachment with file upload.

    Args:
        attachment_data: Attachment data including user_id, title, and file.
        service: Attachment service dependency.

    Returns:
        AttachmentResponse: Created attachment.
    """
    return await service.create_attachment(attachment_data, attachment_data.file)


@router.put(
    "/{attachment_id}",
    response_model=AttachmentResponse,
    status_code=200,
    description="Attachment endpoint to update an attachment.",
)
async def update_attachment(
    attachment_id: UUID,
    title: str | None = Form(None),
    description: str | None = Form(None),
    file: UploadFile | None = File(None),
    service: AttachmentService = Depends(AttachmentService),
) -> AttachmentResponse:
    """
    Attachment endpoint to update an attachment.

    Args:
        attachment_id: Attachment id.
        title: Attachment title.
        description: Attachment description.
        file: New attachment file (optional).
        service: Attachment service dependency.

    Returns:
        AttachmentResponse: Updated attachment.
    """
    logger.info("Updating attachment")
    logger.info(f"Attachment id: {attachment_id}")
    logger.info(f"Service: {service}")

    update_data = {}
    if title is not None:
        update_data["title"] = title
    if description is not None:
        update_data["description"] = description

    attachment_data = AttachmentUpdateRequest(**update_data)

    return await service.update_attachment(attachment_id, attachment_data, file)


@router.delete(
    "/{attachment_id}",
    status_code=204,
    description="Attachment endpoint to delete an attachment.",
)
async def delete_attachment(
    attachment_id: UUID,
    service: AttachmentService = Depends(AttachmentService),
) -> None:
    """
    Attachment endpoint to delete an attachment.

    Args:
        attachment_id: Attachment id.
        service: Attachment service dependency.

    Returns:
        None.
    """
    logger.info("Deleting attachment")
    logger.info(f"Attachment id: {attachment_id}")
    logger.info(f"Service: {service}")
    return await service.delete_attachment(attachment_id)
