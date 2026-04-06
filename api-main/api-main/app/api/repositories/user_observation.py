"""User Observation repository."""

from uuid import UUID

import structlog
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.models.user import User
from app.api.models.user_observation import UserObservation
from app.api.schemas.user_observation import (
    OwnerSummary,
    UserObservationCreateRequest,
    UserObservationHistoryItem,
    UserObservationHistoryResponse,
    UserObservationResponse,
)
from app.core.exceptions import NotFoundException
from app.db.session import AsyncSession, get_db_session

logger = structlog.get_logger(__name__)


class UserObservationRepository:
    """User Observation repository."""

    def __init__(self, db: AsyncSession = Depends(get_db_session)):
        self.db = db

    async def get_observations_by_target_user(
        self, target_user_id: UUID
    ) -> UserObservationHistoryResponse:
        """Get all observations for a target user, formatted as history."""
        logger.debug(f"get_observations_by_target_user called for target_user_id={target_user_id}")

        query = (
            select(UserObservation)
            .where(UserObservation.target_user_id == target_user_id)
            .options(
                selectinload(UserObservation.owner).selectinload(User.profession)
            )
            .order_by(UserObservation.created_at.desc())
        )
        result = await self.db.execute(query)
        observations = result.scalars().all()
        logger.debug(
            f"Retrieved {len(observations)} observations for target_user_id={target_user_id}"
        )

        items = []
        for obs in observations:
            owner_user = obs.owner
            owner_summary = OwnerSummary(
                id=owner_user.id,
                first_name=owner_user.first_name,
                last_name=owner_user.last_name,
                profile_picture=owner_user.profile_picture,
                profession=owner_user.profession.name if owner_user.profession else None,
            )
            items.append(
                UserObservationHistoryItem(
                    id=obs.id,
                    owner=owner_summary,
                    observation=obs.observation,
                    created_at=obs.created_at,
                )
            )

        return UserObservationHistoryResponse(
            target_user_id=target_user_id,
            total=len(items),
            observations=items,
        )

    async def get_observation_by_id(self, observation_id: UUID) -> UserObservationResponse:
        """Get a user observation by id."""
        logger.debug(f"get_observation_by_id called for observation_id={observation_id}")

        query = select(UserObservation).where(UserObservation.id == observation_id)
        result = await self.db.execute(query)
        observation = result.scalar_one_or_none()
        logger.debug(f"Observation found: {observation is not None}")

        if not observation:
            raise NotFoundException("User observation not found")

        return UserObservationResponse.model_validate(observation)

    async def create_observation(
        self, observation_data: UserObservationCreateRequest
    ) -> UserObservationResponse:
        """Create a user observation."""
        logger.debug("create_observation called")

        new_observation = UserObservation(**observation_data.model_dump())
        self.db.add(new_observation)
        await self.db.commit()
        await self.db.refresh(new_observation)

        return UserObservationResponse.model_validate(new_observation)

    async def delete_observation(self, observation_id: UUID) -> None:
        """Delete a user observation."""
        logger.debug(f"delete_observation called for observation_id={observation_id}")

        query = select(UserObservation).where(UserObservation.id == observation_id)
        result = await self.db.execute(query)
        observation = result.scalar_one_or_none()

        if not observation:
            raise NotFoundException("User observation not found")

        await self.db.delete(observation)
        await self.db.commit()
