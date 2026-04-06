"""User specialty validator module."""

from uuid import UUID

import structlog

logger = structlog.get_logger(__name__)


class UserSpecialtyValidator:
    """User specialty validator."""

    @staticmethod
    def validate_user_id(user_id: UUID) -> bool:
        """
        Validate user ID format.

        Args:
            user_id: User ID to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not user_id:
            return False

        return len(str(user_id)) == 36

    @staticmethod
    def validate_specialty_id(specialty_id: UUID) -> bool:
        """
        Validate specialty ID format.

        Args:
            specialty_id: Specialty ID to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not specialty_id:
            return False

        return len(str(specialty_id)) == 36
