"""Professional Location Binding service module."""

from uuid import UUID

import structlog
from fastapi import Depends, HTTPException

from app.api.models.professional_location_binding import ProfessionalLocationBinding
from app.api.repositories.institutions import InstitutionRepository
from app.api.repositories.professional_location_binding import ProfessionalLocationBindingRepository
from app.api.repositories.user import UserRepository
from app.api.schemas.professional_location_binding import (
    ProfessionalLocationBindingCreate,
    ProfessionalLocationBindingResponse,
    ProfessionalLocationBindingUpdate,
)
from app.api.services.attachment import AttachmentService

logger = structlog.get_logger(__name__)


class ProfessionalLocationBindingService:
    """Professional Location Binding service."""

    def __init__(
        self,
        repository: ProfessionalLocationBindingRepository = Depends(ProfessionalLocationBindingRepository),
        user_repository: UserRepository = Depends(UserRepository),
        institution_repository: InstitutionRepository = Depends(InstitutionRepository),
        attachment_service: AttachmentService = Depends(AttachmentService),
    ):
        self.repository = repository
        self.user_repository = user_repository
        self.institution_repository = institution_repository
        self.attachment_service = attachment_service

    async def _enrich_binding_with_attachment(self, binding: ProfessionalLocationBinding) -> ProfessionalLocationBinding:
        """Enrich binding with its contract attachment."""
        attachments = await self.attachment_service.get_attachments_by_entity(binding.id, "professional_location_binding")
        if attachments:
            binding.contract_attachment = attachments[0]
        else:
            binding.contract_attachment = None
        return binding

    async def create_binding(self, binding_in: ProfessionalLocationBindingCreate, created_by: UUID) -> ProfessionalLocationBinding:
        """Create a new professional location binding."""
        # Check if user exists
        user = await self.user_repository.get_user_by_id(binding_in.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if institution exists
        institution = await self.institution_repository.get_by_id(binding_in.institution_id)
        if not institution:
            raise HTTPException(status_code=404, detail="Institution not found")

        # Check for duplicate
        is_duplicate = await self.repository.check_duplicate(binding_in.user_id, binding_in.institution_id)
        if is_duplicate:
            raise HTTPException(status_code=400, detail="Ja existe um vinculo ativo para este profissional e localidade")

        # Validate sectors
        valid_sectors = await self.repository.find_sectors(binding_in.sector_ids, binding_in.institution_id)
        if len(valid_sectors) != len(set(binding_in.sector_ids)):
            raise HTTPException(
                status_code=400,
                detail="One or more sectors are invalid or do not belong to the institution."
            )

        # Create binding
        binding = ProfessionalLocationBinding(
            user_id=binding_in.user_id,
            institution_id=binding_in.institution_id,
            contract_type=binding_in.contract_type,
            status=binding_in.status,
            created_by=created_by,
        )
        await self.repository.create(binding)

        # Save linked sectors
        await self.repository.replace_sectors(binding.id, binding_in.sector_ids)
        await self.repository.db.commit()

        # Load populated entity
        binding = await self.repository.get_by_id_with_relations(binding.id)
        return await self._enrich_binding_with_attachment(binding)

    async def get_bindings(self, user_id: UUID | None = None) -> list[ProfessionalLocationBinding]:
        """List professional location bindings."""
        if user_id:
            bindings = await self.repository.get_by_user_id(user_id)
        else:
            bindings = await self.repository.get_all_bindings()

        return [await self._enrich_binding_with_attachment(binding) for binding in bindings]

    async def get_binding_by_id(self, binding_id: UUID) -> ProfessionalLocationBinding:
        """Get a specific binding by ID."""
        binding = await self.repository.get_by_id_with_relations(binding_id)
        if not binding:
            raise HTTPException(status_code=404, detail="Binding not found")
        return await self._enrich_binding_with_attachment(binding)

    async def update_binding(self, binding_id: UUID, binding_in: ProfessionalLocationBindingUpdate) -> ProfessionalLocationBinding:
        """Update a professional location binding."""
        binding = await self.repository.get_by_id(binding_id)
        if not binding:
            raise HTTPException(status_code=404, detail="Binding not found")

        # Update base fields
        update_data = {}
        if binding_in.contract_type is not None:
            update_data["contract_type"] = binding_in.contract_type
        if binding_in.status is not None:
            update_data["status"] = binding_in.status
            
        if update_data:
            for field, value in update_data.items():
                setattr(binding, field, value)

        # Update sectors if requested
        if binding_in.sector_ids is not None:
            valid_sectors = await self.repository.find_sectors(binding_in.sector_ids, binding.institution_id)
            if len(valid_sectors) != len(set(binding_in.sector_ids)):
                raise HTTPException(
                    status_code=400,
                    detail="One or more sectors are invalid or do not belong to the institution."
                )
            await self.repository.replace_sectors(binding.id, binding_in.sector_ids)

        await self.repository.db.commit()

        # Load populated entity
        binding = await self.repository.get_by_id_with_relations(binding.id)
        return await self._enrich_binding_with_attachment(binding)

    async def delete_binding(self, binding_id: UUID) -> None:
        """Delete a professional location binding."""
        binding = await self.repository.get_by_id(binding_id)
        if not binding:
            raise HTTPException(status_code=404, detail="Binding not found")
            
        await self.repository.delete(binding_id)
        await self.repository.db.commit()
