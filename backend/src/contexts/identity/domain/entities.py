"""Entidades del contexto identity. Cero imports de framework."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4


class Role(StrEnum):
    OWNER = "owner"
    MANAGER = "manager"
    HOST = "host"
    SUPER_ADMIN = "super_admin"


class Plan(StrEnum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class Organization:
    """Restaurante o grupo de restaurantes que comparten cuenta."""

    id: UUID
    name: str
    slug: str
    plan: Plan = Plan.FREE
    created_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def new(cls, name: str, slug: str) -> "Organization":
        return cls(id=uuid4(), name=name, slug=slug)


@dataclass
class Membership:
    """Vincula un user (auth.users) con una Organization en un Role."""

    id: UUID
    user_id: UUID  # FK lógico a auth.users de Supabase
    organization_id: UUID
    role: Role
    created_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def new(cls, user_id: UUID, organization_id: UUID, role: Role) -> "Membership":
        return cls(
            id=uuid4(),
            user_id=user_id,
            organization_id=organization_id,
            role=role,
        )


@dataclass
class UserProfile:
    """Perfil del usuario combinando auth.users + sus memberships."""

    user_id: UUID
    email: str
    memberships: list[Membership]
    organizations: list[Organization]
