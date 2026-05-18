"""DI: construye use cases con repos inyectados."""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.db.session import get_db

from ..application.use_cases import (
    CreateOrganizationWithOwnerUseCase,
    GetMyProfileUseCase,
)
from ..infrastructure.repositories import (
    SqlAlchemyMembershipRepository,
    SqlAlchemyOrganizationRepository,
)


def get_create_org_use_case(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CreateOrganizationWithOwnerUseCase:
    return CreateOrganizationWithOwnerUseCase(
        orgs=SqlAlchemyOrganizationRepository(db),
        memberships=SqlAlchemyMembershipRepository(db),
    )


def get_my_profile_use_case(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> GetMyProfileUseCase:
    return GetMyProfileUseCase(
        orgs=SqlAlchemyOrganizationRepository(db),
        memberships=SqlAlchemyMembershipRepository(db),
    )
