"""Profession validator module."""

import structlog

logger = structlog.get_logger(__name__)


class ProfessionValidator:
    """Profession validator."""

    @staticmethod
    def validate_name(name: str) -> bool:
        """
        Validate profession name.

        Args:
            name: Profession name to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not name or not name.strip():
            return False

        return len(name.strip()) >= 2 and len(name.strip()) <= 255

    @staticmethod
    def validate_description(description: str | None) -> bool:
        """
        Validate profession description.

        Args:
            description: Description to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if description is None:
            return True

        return True
