import re
from typing import TYPE_CHECKING
from uuid import UUID

import structlog

from app.api.schemas.institutions import InstitutionRequest
from app.api.validators.address import AddressValidator
from app.core.cnpj import Cnpj
from app.core.exceptions import ValidationException

if TYPE_CHECKING:
    from app.api.repositories.institutions import InstitutionRepository

logger = structlog.get_logger(__name__)


class InstitutionValidator:
    """Business validation for institutions."""

    CNPJ_LENGTH = 18
    CNPJ_REGEX = re.compile(r"^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$")

    @staticmethod
    async def validate(
        institution: InstitutionRequest,
    ) -> None:
        """Validate complete institution data."""
        InstitutionValidator.validate_tax_document(institution.tax_document)

        if institution.address:
            AddressValidator.validate(institution.address)

    @staticmethod
    def validate_tax_document(tax_document: str | Cnpj) -> None:
        """
        Validate CNPJ format and check digit.

        Args:
            tax_document: The CNPJ to validate (format: 00.000.000/0000-00 or 00000000000000)

        Raises:
            ValidationException: If CNPJ format is invalid
        """
        from app.core.cnpj import Cnpj

        if isinstance(tax_document, Cnpj):
            return

        if not Cnpj.validate(tax_document):
            raise ValidationException("Invalid CNPJ")

    @staticmethod
    async def validate_unique_tax_document(
        tax_document: str | Cnpj,
        repository: "InstitutionRepository",
        exclude_id: UUID | None = None,
    ) -> None:
        """
        Validate tax document is unique in the database.

        Args:
            tax_document: The CNPJ to validate
            repository: The institution repository
            exclude_id: Optional ID to exclude from validation (for updates)

        Raises:
            ValidationException: If tax document already exists
        """
        from app.core.cnpj import Cnpj

        if isinstance(tax_document, Cnpj):
            cnpj_value = tax_document.value
        else:
            cnpj_value = Cnpj._clean(tax_document)

        institutions = await repository.get_institutions()
        for inst in institutions:
            if inst.tax_document.value == cnpj_value and inst.id != exclude_id:
                raise ValidationException(
                    f"Institution with tax document {tax_document} already exists"
                )
