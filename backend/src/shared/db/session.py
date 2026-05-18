"""SQLAlchemy async session factory.

MVP: usamos service_role para todas las queries del backend. RLS sigue ON en DB
pero como el service_role bypasea RLS, el aislamiento multi-tenant se hace en
código vía `WHERE organization_id = :tenant.organization_id` en cada query
(enforced por TenantManager o por revisión manual).

Iteración futura (cuando esté el plomado completo):
- Cambiar a setear `request.jwt.claims` en la conexión Postgres con el JWT del
  user, así RLS aplica automáticamente y el código es más limpio.
- Mientras tanto, la simplicidad de service_role gana al MVP.
"""
from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.shared.settings import settings

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def _build_engine() -> AsyncEngine:
    """Crea engine async. Conexión via Supabase pooler (transaction mode, port 6543)."""
    if not settings.database_url:
        raise RuntimeError(
            "DATABASE_URL not configured. Set it in .env from Supabase Settings → Database."
        )
    # SQLAlchemy quiere `postgresql+psycopg://...` o `postgresql+asyncpg://...`.
    # Supabase da `postgresql://...` — lo convertimos a psycopg async.
    url = settings.database_url
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)

    return create_async_engine(
        url,
        echo=False,
        pool_size=2,
        max_overflow=4,
        pool_pre_ping=True,
        pool_recycle=300,
    )


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        _engine = _build_engine()
    return _engine


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return _sessionmaker


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency: cede una AsyncSession y la cierra al final del request."""
    sm = get_sessionmaker()
    async with sm() as session:
        yield session
