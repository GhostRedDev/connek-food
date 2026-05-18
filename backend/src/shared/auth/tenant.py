"""TenantContext — usuario + organización activa para un request."""
from __future__ import annotations

from dataclasses import dataclass

from src.shared.auth.jwt import SupabaseUser


@dataclass(frozen=True)
class TenantContext:
    """Contexto que cualquier use case necesita para operar dentro de una org.

    - `user`: usuario autenticado (de Supabase Auth).
    - `organization_id`: org activa (la elige el frontend en header X-Organization-Id).
    - `role`: rol del usuario en esa org (owner/manager/host/super_admin).
    """

    user: SupabaseUser
    organization_id: str
    role: str

    @property
    def is_owner(self) -> bool:
        return self.role == "owner"

    @property
    def is_super_admin(self) -> bool:
        return self.role == "super_admin"

    def has_role(self, *roles: str) -> bool:
        return self.role in roles
