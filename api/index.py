"""Vercel Function: modular monolith de toda la API (/api/v1/*).

Single function en MVP — el split a microservicios queda para Pro plan.
Clean Architecture intacta dentro de backend/src/contexts/<x>/.
"""
from __future__ import annotations

import os
import sys
from typing import Any

# Hacer backend/src/ importable.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.shared.errors import register_exception_handlers
from src.shared.settings import settings
from src.shared.telemetry import init_sentry, setup_logging

# ─── Routers de bounded contexts ─────────────────────────────────
from src.contexts.identity.interface.router import router as identity_router

# Cuando aterricen más contexts, agregar aquí:
# from src.contexts.restaurants.interface.router    import router as restaurants_router
# from src.contexts.reservations.interface.router   import router as reservations_router
# ...

setup_logging()
init_sentry(service_name="connek-api")

app = FastAPI(
    title="Connek Restaurant OS API",
    version="0.1.0",
    description="Backend monolítico modular. Clean Arch en backend/src/contexts/<x>/.",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins + ["*"],  # MVP — restringir en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

# Montaje de routers — cada uno bajo su prefix
app.include_router(identity_router, prefix="/api/v1/identity")

# Pendientes (placeholders hasta que aterricen):
# app.include_router(restaurants_router,    prefix="/api/v1/restaurants",    tags=["restaurants"])
# app.include_router(reservations_router,   prefix="/api/v1/reservations",   tags=["reservations"])
# app.include_router(floor_router,          prefix="/api/v1/floor",          tags=["floor"])
# app.include_router(waitlist_router,       prefix="/api/v1/waitlist",       tags=["waitlist"])
# app.include_router(clients_router,        prefix="/api/v1/clients",        tags=["clients"])
# app.include_router(communications_router, prefix="/api/v1/communications", tags=["communications"])
# app.include_router(reviews_router,        prefix="/api/v1/reviews",        tags=["reviews"])
# app.include_router(ai_router,             prefix="/api/v1/ai",             tags=["ai"])
# app.include_router(staff_router,          prefix="/api/v1/staff",          tags=["staff"])
# app.include_router(billing_router,        prefix="/api/v1/billing",        tags=["billing"])
# app.include_router(admin_router,          prefix="/api/v1/admin",          tags=["admin"])

IMPLEMENTED_CONTEXTS = ["identity"]
PENDING_CONTEXTS = [
    "restaurants", "reservations", "floor", "waitlist",
    "clients", "communications", "reviews", "ai", "staff", "billing", "admin",
]


@app.get("/api/v1", include_in_schema=False)
@app.get("/api/v1/", include_in_schema=False)
def api_root() -> dict[str, Any]:
    return {
        "service": "connek-api",
        "version": app.version,
        "env": settings.env,
        "implemented": IMPLEMENTED_CONTEXTS,
        "pending": PENDING_CONTEXTS,
        "docs": "/api/v1/docs",
    }


@app.get("/api/v1/{context}/{path:path}", include_in_schema=False)
def placeholder_for_pending_context(context: str, path: str, request: Request) -> dict[str, Any]:
    """Placeholder para contexts aún no implementados."""
    if context in IMPLEMENTED_CONTEXTS:
        # Si llegamos aquí es porque el router del contexto NO matchea ese path interno.
        return {"status": "not_found", "context": context, "path": path}
    return {
        "service": "connek-api",
        "status": "not_implemented",
        "context": context,
        "known_context": context in PENDING_CONTEXTS,
        "path": path,
        "method": request.method,
    }
