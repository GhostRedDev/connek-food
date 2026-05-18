"""Excepciones de dominio + handler global FastAPI.

Cada contexto puede subclasear DomainError. El handler global mapea a HTTP.
"""
from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class DomainError(Exception):
    """Base de errores de negocio. Mapea a HTTP 400 por default."""

    http_status: int = 400
    code: str = "domain_error"

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class NotFoundError(DomainError):
    http_status = 404
    code = "not_found"


class ForbiddenError(DomainError):
    http_status = 403
    code = "forbidden"


class UnauthorizedError(DomainError):
    http_status = 401
    code = "unauthorized"


class ConflictError(DomainError):
    http_status = 409
    code = "conflict"


class InvalidStateTransition(ConflictError):
    code = "invalid_state_transition"


class ValidationError(DomainError):
    http_status = 422
    code = "validation_error"


def register_exception_handlers(app: FastAPI) -> None:
    """Registra el handler global. Llamar al construir FastAPI."""

    @app.exception_handler(DomainError)
    async def domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:  # noqa: RUF029
        return JSONResponse(
            status_code=exc.http_status,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )
