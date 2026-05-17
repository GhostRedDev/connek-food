"""Vercel Function placeholder — context: communications.

Cuando implementes este contexto:
1. Crea src/contexts/communications/interface/router.py
2. Importa el router aquí
3. Reemplaza el endpoint placeholder
4. Activa init_sentry
"""
from __future__ import annotations

from fastapi import FastAPI

# from src.shared.telemetry import init_sentry
# from src.contexts.communications.interface.router import router

# init_sentry(service_name="communications")

app = FastAPI(title="Connek · communications")


@app.get("/api/v1/communications/")
def root() -> dict[str, str]:
    return {"service": "communications", "status": "not_implemented"}


# app.include_router(router, prefix="/api/v1")
