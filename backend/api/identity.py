"""Vercel Function placeholder — context: identity.

Cuando implementes este contexto:
1. Crea src/contexts/identity/interface/router.py
2. Importa el router aquí
3. Reemplaza el endpoint placeholder
4. Activa init_sentry
"""
from __future__ import annotations

from fastapi import FastAPI

# from src.shared.telemetry import init_sentry
# from src.contexts.identity.interface.router import router

# init_sentry(service_name="identity")

app = FastAPI(title="Connek · identity")


@app.get("/api/v1/identity/")
def root() -> dict[str, str]:
    return {"service": "identity", "status": "not_implemented"}


# app.include_router(router, prefix="/api/v1")
