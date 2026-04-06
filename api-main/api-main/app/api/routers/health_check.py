"""Health check router module."""

import fastapi

from app.api.schemas.health_check import HealthCheckResponse

router = fastapi.APIRouter()


@router.get(
    "",
    response_model=HealthCheckResponse,
    status_code=200,
    description="Health check endpoint",
)
async def health_check() -> HealthCheckResponse:
    """
    Health check endpoint to verify API status.

    Returns:
        HealthCheckResponse: Status indicator showing the API is operational.
    """
    return HealthCheckResponse(status="ok")
