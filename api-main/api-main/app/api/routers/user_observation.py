"""User Observation router module."""

from uuid import UUID

import fastapi
import structlog
from fastapi import Depends

from app.api.schemas.user_observation import (
    UserObservationCreateRequest,
    UserObservationHistoryResponse,
    UserObservationResponse,
)
from app.api.services.user_observation import UserObservationService

logger = structlog.get_logger(__name__)

router = fastapi.APIRouter()


@router.get(
    "/target/{target_user_id}",
    response_model=UserObservationHistoryResponse,
    status_code=200,
    description="Retorna o histórico de observações feitas sobre um determinado usuário.",
)
async def get_observations_by_target_user(
    target_user_id: UUID,
    service: UserObservationService = Depends(UserObservationService),
) -> UserObservationHistoryResponse:
    """
    Retorna o histórico de observações de um usuário alvo.

    Args:
        target_user_id: ID do usuário alvo.
        service: User Observation service dependency.

    Returns:
        UserObservationHistoryResponse: Histórico de observações.
    """
    logger.info(f"Getting observations for target_user_id={target_user_id}")
    return await service.get_observations_by_target_user(target_user_id)


@router.get(
    "/{observation_id}",
    response_model=UserObservationResponse,
    status_code=200,
    description="Retorna uma observação pelo seu ID.",
)
async def get_observation_by_id(
    observation_id: UUID,
    service: UserObservationService = Depends(UserObservationService),
) -> UserObservationResponse:
    """
    Retorna uma observação pelo seu ID.

    Args:
        observation_id: ID da observação.
        service: User Observation service dependency.

    Returns:
        UserObservationResponse: Observação encontrada.
    """
    logger.info(f"Getting observation by id={observation_id}")
    return await service.get_observation_by_id(observation_id)


@router.post(
    "",
    response_model=UserObservationResponse,
    status_code=201,
    description="Cria uma nova observação sobre um usuário.",
)
async def create_observation(
    observation: UserObservationCreateRequest,
    service: UserObservationService = Depends(UserObservationService),
) -> UserObservationResponse:
    """
    Cria uma nova observação sobre um usuário.

    Args:
        observation: Dados da observação.
        service: User Observation service dependency.

    Returns:
        UserObservationResponse: Observação criada.
    """
    logger.info("Creating user observation")
    return await service.create_observation(observation)


@router.delete(
    "/{observation_id}",
    status_code=204,
    description="Remove uma observação pelo seu ID.",
)
async def delete_observation(
    observation_id: UUID,
    service: UserObservationService = Depends(UserObservationService),
) -> None:
    """
    Remove uma observação pelo seu ID.

    Args:
        observation_id: ID da observação.
        service: User Observation service dependency.

    Returns:
        None.
    """
    logger.info(f"Deleting observation id={observation_id}")
    return await service.delete_observation(observation_id)
