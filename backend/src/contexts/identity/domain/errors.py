"""Errores de dominio del contexto identity."""
from __future__ import annotations

from src.shared.errors import ConflictError, NotFoundError


class OrganizationNotFound(NotFoundError):
    code = "organization_not_found"


class MembershipNotFound(NotFoundError):
    code = "membership_not_found"


class SlugAlreadyTaken(ConflictError):
    code = "slug_already_taken"
