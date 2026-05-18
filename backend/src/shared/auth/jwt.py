"""Validación de JWT de Supabase Auth.

Supabase firma JWTs con HS256 + el shared `JWT Secret` del proyecto.
Cualquier endpoint protegido extrae el header `Authorization: Bearer <jwt>`,
verifica firma+expiración, y devuelve el `SupabaseUser` con `sub` (user_id).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import jwt as pyjwt

from src.shared.errors import UnauthorizedError
from src.shared.settings import settings


@dataclass(frozen=True)
class SupabaseUser:
    """Representación mínima del usuario autenticado por Supabase."""

    id: str  # auth.users.id (UUID)
    email: str | None
    role: str  # claim 'role', típicamente 'authenticated'
    raw_claims: dict[str, Any]


def decode_supabase_jwt(token: str) -> SupabaseUser:
    """Valida firma + expiración + audience del JWT y devuelve SupabaseUser.

    Raises:
        UnauthorizedError: si el token es inválido, expiró, o audience incorrecta.
    """
    if not settings.supabase_jwt_secret:
        raise UnauthorizedError(
            "Server missing SUPABASE_JWT_SECRET configuration",
            details={"hint": "set SUPABASE_JWT_SECRET env var"},
        )

    try:
        claims = pyjwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_audience,
        )
    except pyjwt.ExpiredSignatureError as e:
        raise UnauthorizedError("Token expired") from e
    except pyjwt.InvalidTokenError as e:
        raise UnauthorizedError(f"Invalid token: {e}") from e

    user_id = claims.get("sub")
    if not user_id:
        raise UnauthorizedError("Token missing 'sub' claim")

    return SupabaseUser(
        id=user_id,
        email=claims.get("email"),
        role=claims.get("role", "authenticated"),
        raw_claims=claims,
    )
