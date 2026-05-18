"""Implementaciones SQLAlchemy de los Protocols del dominio."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.entities import Membership, Organization, Plan, Role
from .models import MembershipModel, OrganizationModel


def _to_org_entity(m: OrganizationModel) -> Organization:
    return Organization(
        id=m.id,
        name=m.name,
        slug=m.slug,
        plan=Plan(m.plan),
        created_at=m.created_at,
    )


def _to_membership_entity(m: MembershipModel) -> Membership:
    return Membership(
        id=m.id,
        user_id=m.user_id,
        organization_id=m.organization_id,
        role=Role(m.role),
        created_at=m.created_at,
    )


class SqlAlchemyOrganizationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get(self, id: UUID) -> Organization | None:
        row = await self._s.get(OrganizationModel, id)
        return _to_org_entity(row) if row else None

    async def get_by_slug(self, slug: str) -> Organization | None:
        stmt = select(OrganizationModel).where(OrganizationModel.slug == slug)
        row = (await self._s.execute(stmt)).scalar_one_or_none()
        return _to_org_entity(row) if row else None

    async def save(self, org: Organization) -> None:
        existing = await self._s.get(OrganizationModel, org.id)
        if existing is None:
            self._s.add(
                OrganizationModel(
                    id=org.id,
                    name=org.name,
                    slug=org.slug,
                    plan=org.plan.value,
                )
            )
        else:
            existing.name = org.name
            existing.slug = org.slug
            existing.plan = org.plan.value
        await self._s.commit()

    async def list_for_user(self, user_id: UUID) -> list[Organization]:
        stmt = (
            select(OrganizationModel)
            .join(MembershipModel, MembershipModel.organization_id == OrganizationModel.id)
            .where(MembershipModel.user_id == user_id)
            .order_by(OrganizationModel.created_at.asc())
        )
        rows = (await self._s.execute(stmt)).scalars().all()
        return [_to_org_entity(r) for r in rows]


class SqlAlchemyMembershipRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get(self, id: UUID) -> Membership | None:
        row = await self._s.get(MembershipModel, id)
        return _to_membership_entity(row) if row else None

    async def list_for_user(self, user_id: UUID) -> list[Membership]:
        stmt = (
            select(MembershipModel)
            .where(MembershipModel.user_id == user_id)
            .order_by(MembershipModel.created_at.asc())
        )
        rows = (await self._s.execute(stmt)).scalars().all()
        return [_to_membership_entity(r) for r in rows]

    async def list_for_organization(self, organization_id: UUID) -> list[Membership]:
        stmt = (
            select(MembershipModel)
            .where(MembershipModel.organization_id == organization_id)
            .order_by(MembershipModel.created_at.asc())
        )
        rows = (await self._s.execute(stmt)).scalars().all()
        return [_to_membership_entity(r) for r in rows]

    async def save(self, m: Membership) -> None:
        existing = await self._s.get(MembershipModel, m.id)
        if existing is None:
            self._s.add(
                MembershipModel(
                    id=m.id,
                    user_id=m.user_id,
                    organization_id=m.organization_id,
                    role=m.role.value,
                )
            )
        else:
            existing.role = m.role.value
        await self._s.commit()
