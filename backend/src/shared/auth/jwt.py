"""Validación de JWT de Supabase Auth.

Supabase Auth firma JWTs con ES256 (claves asimétricas) por default en
proyectos nuevos, o HS256 (secret simétrico) en proyectos legacy.

- ES256/RS256/EdDSA → verificamos con la public key del JWKS endpoint.
- HS256             → verificamos con SUPABASE_JWT_SECRET.

El JWKS se cachea en memoria por el process (warm function reuse).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import jwt as pyjwt
from jwt import PyJWKClient

from src.shared.errors import UnauthorizedError
from src.shared.settings import settings

_ASYMMETRIC_ALGS = {"ES256", "ES384", "RS256", "RS384", "EdDSA"}
_SYMMETRIC_ALGS = {"HS256", "HS384", "HS512"}

_jwks_client: PyJWKClient | None = None


def _get_jwks_client() -> PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        if not settings.supabase_url:
            raise UnauthorizedError("Server missing SUPABASE_URL configuration")
        jwks_url = f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
        _jwks_client = PyJWKClient(jwks_url, cache_keys=True, lifespan=300)
    return _jwks_client


@dataclass(frozen=True)
class SupabaseUser:
    id: str
    email: str | None
    role: str
    raw_claims: dict[str, Any]


def decode_supabase_jwt(token: str) -> SupabaseUser:
    """Valida firma + expiración + audience del JWT.

    Auto-detecta el algoritmo desde el header del token y elige verificación
    asimétrica (JWKS) o simétrica (HS256 secret).
    """
    try:
        unverified_header = pyjwt.get_unverified_header(token)
    except pyjwt.InvalidTokenError as e:
        raise UnauthorizedError(f"Malformed token header: {e}") from e

    alg = unverified_header.get("alg", "")

    try:
        if alg in _ASYMMETRIC_ALGS:
            signing_key = _get_jwks_client().get_signing_key_from_jwt(token).key
            claims = pyjwt.decode(
                token,
                signing_key,
                algorithms=list(_ASYMMETRIC_ALGS),
                audience=settings.jwt_audience,
            )
        elif alg in _SYMMETRIC_ALGS:
            if not settings.supabase_jwt_secret:
                raise UnauthorizedError(
                    "Server missing SUPABASE_JWT_SECRET for HS-algo tokens"
                )
            claims = pyjwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=list(_SYMMETRIC_ALGS),
                audience=settings.jwt_audience,
            )
        else:
            raise UnauthorizedError(f"Unsupported JWT algorithm: {alg}")
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
