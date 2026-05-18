"""Vercel Function: modular monolith de toda la API (/api/v1/*).

Single function en MVP — el split a microservicios queda para Pro plan.
Clean Architecture intacta dentro de backend/src/contexts/<x>/.
"""
from __future__ import annotations

import os
import sys
from typing import Any

# Hacer backend/src/ importable cuando los contexts existan.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from fastapi import FastAPI, Request

app = FastAPI(
    title="Connek Restaurant OS API",
    version="0.1.0",
    description="Backend monolítico modular. Cada bounded context en backend/src/contexts/<x>/.",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
)

CONTEXTS = [
    "identity", "restaurants", "reservations", "floor", "waitlist",
    "clients", "communications", "reviews", "ai", "staff", "billing", "admin",
]

# Routers de cada bounded context — descomentar a medida que se implementen.
# from src.contexts.identity.interface.router       import router as identity_router
# from src.contexts.restaurants.interface.router    import router as restaurants_router
# ...
# app.include_router(identity_router,    prefix="/api/v1/identity",    tags=["identity"])
# app.include_router(restaurants_router, prefix="/api/v1/restaurants", tags=["restaurants"])


@app.get("/api/v1")
@app.get("/api/v1/")
def api_root() -> dict[str, Any]:
    return {
        "service": "connek-api",
        "version": app.version,
        "status": "not_implemented",
        "contexts": CONTEXTS,
        "docs": "/api/v1/docs",
    }


@app.get("/api/v1/{full_path:path}")
def context_placeholder(full_path: str, request: Request) -> dict[str, Any]:
    """Placeholder hasta que cada context monte su router real."""
    context = full_path.split("/", 1)[0] if full_path else None
    known = context in CONTEXTS
    return {
        "service": "connek-api",
        "status": "not_implemented",
        "context": context,
        "known_context": known,
        "path": full_path,
        "method": request.method,
        "message": (
            f"El bounded context '{context}' aún no tiene router implementado. "
            "Ver backend/src/contexts/<context>/interface/router.py"
            if known
            else f"Context '{context}' desconocido. Disponibles: {CONTEXTS}"
        ),
    }
