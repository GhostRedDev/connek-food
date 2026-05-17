"""Vercel Function placeholder — context: clients.

Cuando implementes este contexto:
1. Crea src/contexts/clients/interface/router.py
2. Importa el router aquí
3. Reemplaza el endpoint placeholder
4. Activa init_sentry
"""
from __future__ import annotations

from fastapi import FastAPI

# from src.shared.telemetry import init_sentry
# from src.contexts.clients.interface.router import router

# init_sentry(service_name="clients")

app = FastAPI(title="Connek · clients")


@app.get("/api/v1/clients/")
def root() -> dict[str, str]:
    return {"service": "clients", "status": "not_implemented"}


# app.include_router(router, prefix="/api/v1")
