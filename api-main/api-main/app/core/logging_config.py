"""Centralized logging configuration using structlog."""

import logging
import sys
from typing import Any

import structlog

from app.core.config import settings


def configure_logging() -> None:
    """Configure structured logging for the application.

    This function sets up structlog with different configurations based on the environment:
    - Development: Pretty-printed, colorized logs for easy reading
    - Production: JSON-formatted logs for log aggregation systems
    """
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.ENVIRONMENT == "development":
        processors = shared_processors + [structlog.dev.ConsoleRenderer(colors=True)]
    else:
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    if settings.ENVIRONMENT == "production":
        logging.getLogger("uvicorn.access").setLevel(logging.ERROR)
        logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    else:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.error").setLevel(logging.INFO)

    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

    logger = structlog.get_logger(__name__)
    logger.info(
        "logging_configured",
        environment=settings.ENVIRONMENT,
        log_level=settings.LOG_LEVEL,
        log_format="json" if settings.ENVIRONMENT != "development" else "console",
    )


def get_logger(name: str | None = None) -> Any:
    """Get a configured structlog logger.

    Args:
        name: Optional name for the logger. If None, uses the caller's module name.

    Returns:
        A configured structlog logger instance.
    """
    return structlog.get_logger(name)
