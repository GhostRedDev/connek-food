"""DTOs Pydantic para input/output HTTP."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from ..domain.entities import Membership, Organization, UserProfile


# ─── Input ───────────────────────────────────────────────────────


class CreateOrganizationInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)


# ─── Output ──────────────────────────────────────────────────────


class OrganizationOutput(BaseModel):
    id: UUID
    name: str
    slug: str
    plan: str
    created_at: datetime

    @classmethod
    def from_entity(cls, e: Organization) -> "OrganizationOutput":
        return cls(
            id=e.id,
            name=e.name,
            slug=e.slug,
            plan=e.plan.value,
            created_at=e.created_at,
        )


class MembershipOutput(BaseModel):
    id: UUID
    user_id: UUID
    organization_id: UUID
    role: str
    created_at: datetime

    @classmethod
    def from_entity(cls, e: Membership) -> "MembershipOutput":
        return cls(
            id=e.id,
            user_id=e.user_id,
            organization_id=e.organization_id,
            role=e.role.value,
            created_at=e.created_at,
        )


class MeOutput(BaseModel):
    user_id: UUID
    email: str
    memberships: list[MembershipOutput]
    organizations: list[OrganizationOutput]

    @classmethod
    def from_entity(cls, e: UserProfile) -> "MeOutput":
        return cls(
            user_id=e.user_id,
            email=e.email,
            memberships=[MembershipOutput.from_entity(m) for m in e.memberships],
            organizations=[OrganizationOutput.from_entity(o) for o in e.organizations],
        )
