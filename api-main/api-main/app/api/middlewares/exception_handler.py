import traceback

import structlog
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
    ResourceAlreadyExistsException,
    ResourceNotFoundException,
    UnauthorizedException,
    ValidationException,
)

logger = structlog.get_logger(__name__)


async def resource_not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle ResourceNotFoundException."""
    assert isinstance(exc, ResourceNotFoundException)
    logger.warning(
        "resource_not_found",
        resource_name=exc.resource_name,
        resource_id=exc.resource_id,
        path=request.url.path,
    )
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})


async def resource_already_exists_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle ResourceAlreadyExistsException."""
    assert isinstance(exc, ResourceAlreadyExistsException)
    logger.warning(
        "resource_already_exists", resource_name=exc.resource_name, path=request.url.path
    )
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)})


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle ValidationException."""
    assert isinstance(exc, ValidationException)
    logger.warning("validation_exception", path=request.url.path)
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)})


async def not_found_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle NotFoundException."""
    assert isinstance(exc, NotFoundException)
    logger.warning("not_found_exception", message=exc.message, path=request.url.path)
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": exc.message})


async def bad_request_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle BadRequestException."""
    assert isinstance(exc, BadRequestException)
    logger.warning("bad_request_exception", message=exc.message, path=request.url.path)
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": exc.message})


async def unauthorized_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle UnauthorizedException."""
    assert isinstance(exc, UnauthorizedException)
    logger.warning("unauthorized_exception", message=exc.message, path=request.url.path)
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": exc.message})


async def integrity_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle IntegrityError."""
    assert isinstance(exc, IntegrityError)
    logger.warning("integrity_error", error=str(exc), path=request.url.path)

    message = "Erro de integridade no banco de dados."
    if "foreign key constraint" in str(exc.orig):
        message = "Referência a um registro inexistente (chave estrangeira inválida)."
    elif "unique constraint" in str(exc.orig):
        message = "Registro duplicado (violação de unicidade)."

    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": message})


async def custom_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle FastAPI RequestValidationError and translate messages to Portuguese."""
    logger.warning("request_validation_error", path=request.url.path, errors=exc.errors())

    translated_errors = []
    for error in exc.errors():
        field = error["loc"][-1] if len(error["loc"]) > 0 else "unknown"
        error_type = error.get("type", "")
        msg = error.get("msg", "")

        if error_type in ("missing", "value_error.missing") or msg.lower() == "field required":
            msg = f"O campo '{field}' é obrigatório."
        elif error_type == "string_too_short":
            msg = f"O campo '{field}' é muito curto."
        elif error_type == "string_too_long":
            msg = f"O campo '{field}' é muito longo."
        elif error_type in ("int_parsing", "type_error.integer"):
            msg = f"O campo '{field}' deve ser um número inteiro."
        elif error_type in ("uuid_parsing", "type_error.uuid"):
            msg = f"O campo '{field}' deve ser um UUID válido."
        elif error_type in ("float_parsing", "type_error.float"):
            msg = f"O campo '{field}' deve ser um número decimal."
        elif error_type in ("bool_parsing", "type_error.bool"):
            msg = f"O campo '{field}' deve ser um valor booleano."
        elif "valid email" in msg.lower() or error_type == "value_error.email":
            msg = f"O campo '{field}' deve ser um e-mail válido."

        translated_errors.append({"loc": error["loc"], "msg": msg, "type": error_type})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": translated_errors}
    )


async def response_validation_error_handler(
    request: Request, exc: ResponseValidationError
) -> JSONResponse:
    """Handle ResponseValidationError — log full traceback for debugging."""
    tb = traceback.format_exc()
    logger.error(
        "response_validation_error",
        path=str(request.url.path),
        method=request.method,
        traceback=tb,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Erro interno: falha na serialização da resposta."},
    )
