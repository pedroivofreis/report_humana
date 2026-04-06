import os
import time

import structlog
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import IntegrityError

from app.api.main import api_router
from app.api.middlewares.exception_handler import (
    bad_request_exception_handler,
    custom_validation_exception_handler,
    integrity_error_handler,
    not_found_exception_handler,
    resource_already_exists_handler,
    resource_not_found_handler,
    response_validation_error_handler,
    unauthorized_exception_handler,
    validation_exception_handler,
)
from app.api.routers.auth import limiter
from app.core.config import settings
from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
    ResourceAlreadyExistsException,
    ResourceNotFoundException,
    UnauthorizedException,
    ValidationException,
)
from app.core.logging_config import configure_logging
from app.core.middleware.logging_middleware import LoggingMiddleware

configure_logging()
logger = structlog.get_logger(__name__)

# Set timezone
os.environ["TZ"] = settings.TIMEZONE
time.tzset()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_STR}/openapi.json",
    description="Institution and sector Microservice for the Humana project",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Middlewares e Exception Handlers
app.add_middleware(LoggingMiddleware)
app.add_exception_handler(ResourceNotFoundException, resource_not_found_handler)
app.add_exception_handler(ResourceAlreadyExistsException, resource_already_exists_handler)
app.add_exception_handler(ValidationException, validation_exception_handler)
app.add_exception_handler(RequestValidationError, custom_validation_exception_handler)
app.add_exception_handler(NotFoundException, not_found_exception_handler)
app.add_exception_handler(BadRequestException, bad_request_exception_handler)
app.add_exception_handler(UnauthorizedException, unauthorized_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(ResponseValidationError, response_validation_error_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Routers
app.include_router(
    api_router,
    prefix=settings.API_STR,
)


@app.get("/")
async def root() -> dict[str, str]:
    logger.info("root_endpoint_accessed")
    return {"message": "Welcome to the Institution and sector Microservice for the Humana project!"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint with system information."""
    logger.debug("health_check_requested")
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "log_level": settings.LOG_LEVEL,
    }
