"""Use cases del contexto identity.

Reglas Clean Arch:
- Solo importa de domain/ (propio o shared).
- Orquesta repos vía Protocols.
- No conoce FastAPI, SQLAlchemy, Supabase.
"""
from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from ..domain.entities import Membership, Organization, Role, UserProfile
from ..domain.repositories import MembershipRepository, OrganizationRepository


def _slugify(text: str) -> str:
    """Slug muy simple para MVP. Mejorable con python-slugify si necesario."""
    return (
        "".join(c.lower() if c.isalnum() else "-" for c in text.strip())
        .strip("-")
        .replace("--", "-")
    )[:50] or "mi-restaurante"


@dataclass
class CreateOrganizationCommand:
    user_id: UUID
    name: str


class CreateOrganizationWithOwnerUseCase:
    """Crea Organization + Membership(role=owner) en una transacción lógica."""

    def __init__(
        self,
        orgs: OrganizationRepository,
        memberships: MembershipRepository,
    ) -> None:
        self._orgs = orgs
        self._memberships = memberships

    async def execute(self, cmd: CreateOrganizationCommand) -> Organization:
        slug = _slugify(cmd.name)
        # MVP: no garantizamos unicidad de slug aún (lo dejamos al constraint DB).
        org = Organization.new(name=cmd.name, slug=slug)
        await self._orgs.save(org)

        membership = Membership.new(
            user_id=cmd.user_id,
            organization_id=org.id,
            role=Role.OWNER,
        )
        await self._memberships.save(membership)
        return org


class GetMyProfileUseCase:
    """Devuelve perfil del usuario: sus memberships + organizations."""

    def __init__(
        self,
        orgs: OrganizationRepository,
        memberships: MembershipRepository,
    ) -> None:
        self._orgs = orgs
        self._memberships = memberships

    async def execute(self, user_id: UUID, email: str) -> UserProfile:
        ms = await self._memberships.list_for_user(user_id)
        orgs = await self._orgs.list_for_user(user_id)
        return UserProfile(
            user_id=user_id,
            email=email,
            memberships=ms,
            organizations=orgs,
        )
