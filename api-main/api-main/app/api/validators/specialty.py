"""Specialty validator module."""

from uuid import UUID

import structlog

logger = structlog.get_logger(__name__)


class SpecialtyValidator:
    """Specialty validator."""

    @staticmethod
    def validate_name(name: str) -> bool:
        """
        Validate specialty name.

        Args:
            name: Specialty name to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not name or not name.strip():
            return False

        return len(name.strip()) >= 2 and len(name.strip()) <= 255

    @staticmethod
    def validate_description(description: str | None) -> bool:
        """
        Validate specialty description.

        Args:
            description: Description to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if description is None:
            return True

        return True

    @staticmethod
    def validate_profession_id(profession_id: UUID) -> bool:
        """
        Validate profession ID format.

        Args:
            profession_id: Profession ID to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not profession_id:
            return False

        return len(str(profession_id)) == 36
