"""User Observation service module."""

from uuid import UUID

import structlog
from fastapi import Depends

from app.api.repositories.user_observation import UserObservationRepository
from app.api.schemas.user_observation import (
    UserObservationCreateRequest,
    UserObservationHistoryResponse,
    UserObservationResponse,
)

logger = structlog.get_logger(__name__)


class UserObservationService:
    """User Observation service."""

    def __init__(
        self, repository: UserObservationRepository = Depends(UserObservationRepository)
    ):
        self.repository = repository

    async def get_observations_by_target_user(
        self, target_user_id: UUID
    ) -> UserObservationHistoryResponse:
        """Get all observations for a target user as history."""
        logger.debug(f"Get observations for target_user_id={target_user_id}")
        return await self.repository.get_observations_by_target_user(target_user_id)

    async def get_observation_by_id(self, observation_id: UUID) -> UserObservationResponse:
        """Get a user observation by id."""
        logger.debug(f"Get observation by id={observation_id}")
        return await self.repository.get_observation_by_id(observation_id)

    async def create_observation(
        self, observation_data: UserObservationCreateRequest
    ) -> UserObservationResponse:
        """Create a user observation."""
        logger.debug("Create user observation")
        return await self.repository.create_observation(observation_data)

    async def delete_observation(self, observation_id: UUID) -> None:
        """Delete a user observation."""
        logger.debug(f"Delete observation by id={observation_id}")
        return await self.repository.delete_observation(observation_id)
