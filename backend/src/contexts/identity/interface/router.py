"""Router FastAPI del contexto identity."""
from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.shared.auth.dependencies import require_user
from src.shared.auth.jwt import SupabaseUser

from ..application.use_cases import (
    CreateOrganizationCommand,
    CreateOrganizationWithOwnerUseCase,
    GetMyProfileUseCase,
)
from .dependencies import get_create_org_use_case, get_my_profile_use_case
from .dtos import CreateOrganizationInput, MeOutput, OrganizationOutput

router = APIRouter(tags=["identity"])


@router.get("/me", response_model=MeOutput)
async def get_me(
    user: Annotated[SupabaseUser, Depends(require_user)],
    use_case: Annotated[GetMyProfileUseCase, Depends(get_my_profile_use_case)],
) -> MeOutput:
    """Perfil del usuario autenticado: sus memberships + organizations."""
    profile = await use_case.execute(user_id=UUID(user.id), email=user.email or "")
    return MeOutput.from_entity(profile)


@router.post("/organizations", response_model=OrganizationOutput, status_code=status.HTTP_201_CREATED)
async def create_organization(
    body: CreateOrganizationInput,
    user: Annotated[SupabaseUser, Depends(require_user)],
    use_case: Annotated[CreateOrganizationWithOwnerUseCase, Depends(get_create_org_use_case)],
) -> OrganizationOutput:
    """Crea nueva Organization y asigna al usuario como owner.

    Para signup el trigger SQL crea la primera Org automáticamente. Este endpoint
    es para crear orgs adicionales o desde la UI.
    """
    org = await use_case.execute(
        CreateOrganizationCommand(user_id=UUID(user.id), name=body.name)
    )
    return OrganizationOutput.from_entity(org)
