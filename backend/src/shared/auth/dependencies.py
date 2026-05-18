"""FastAPI DI dependencies para auth + tenancy.

Uso típico en un router:
    @router.get("/me")
    async def get_me(user: SupabaseUser = Depends(require_user)) -> ...

    @router.get("/restaurants")
    async def list_restaurants(tenant: TenantContext = Depends(require_tenant)) -> ...

    @router.delete("/reservations/{id}")
    async def cancel(_: TenantContext = Depends(require_role("owner", "manager"))) -> ...
"""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.shared.auth.jwt import SupabaseUser, decode_supabase_jwt
from src.shared.auth.tenant import TenantContext
from src.shared.errors import ForbiddenError, UnauthorizedError

_bearer = HTTPBearer(auto_error=False)


async def require_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> SupabaseUser:
    """Extrae y valida el JWT de Supabase. Lanza 401 si falta/inválido."""
    if creds is None or not creds.credentials:
        raise UnauthorizedError("Missing Bearer token")
    return decode_supabase_jwt(creds.credentials)


async def require_tenant(
    user: Annotated[SupabaseUser, Depends(require_user)],
    organization_id: Annotated[str | None, Header(alias="X-Organization-Id")] = None,
) -> TenantContext:
    """Resuelve la org activa desde header X-Organization-Id.

    NOTA: en esta versión MVP la pertenencia se valida vía RLS (Postgres rechaza
    inserts/selects de orgs ajenas). En siguientes iteraciones se puede agregar
    aquí un lookup explícito a `memberships` para fallar más temprano con 403.
    """
    if not organization_id:
        raise UnauthorizedError(
            "Missing X-Organization-Id header",
            details={"hint": "frontend must send the active org id"},
        )
    # Role placeholder — se reemplaza por lookup real cuando aterrice el repo de memberships.
    return TenantContext(user=user, organization_id=organization_id, role="member")


def require_role(*allowed: str):
    """Factory: dependency que valida que el tenant tenga uno de los roles dados."""

    async def _checker(
        tenant: Annotated[TenantContext, Depends(require_tenant)],
    ) -> TenantContext:
        if tenant.role not in allowed and not tenant.is_super_admin:
            raise ForbiddenError(
                f"Requires one of roles: {allowed}",
                details={"have": tenant.role, "need": list(allowed)},
            )
        return tenant

    return _checker
