"""Logging middleware for request tracking and correlation."""

import time
import uuid
from collections.abc import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to add request logging with correlation IDs and performance tracking."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process each request with logging context and tracking.

        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler

        Returns:
            The HTTP response with correlation ID header
        """
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            correlation_id=correlation_id,
            path=request.url.path,
            method=request.method,
            client_ip=request.client.host if request.client else None,
        )

        logger = structlog.get_logger()
        start_time = time.time()

        try:
            response: Response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000

            logger.info(
                "request_completed",
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )

            response.headers["X-Correlation-ID"] = correlation_id
            return response

        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                "request_failed",
                exc_info=exc,
                error_type=type(exc).__name__,
                duration_ms=round(duration_ms, 2),
            )
            raise
        finally:
            structlog.contextvars.clear_contextvars()
