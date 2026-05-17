"""Vercel Function placeholder — context: floor.

Cuando implementes este contexto:
1. Crea src/contexts/floor/interface/router.py
2. Importa el router aquí
3. Reemplaza el endpoint placeholder
4. Activa init_sentry
"""
from __future__ import annotations

from fastapi import FastAPI

# from src.shared.telemetry import init_sentry
# from src.contexts.floor.interface.router import router

# init_sentry(service_name="floor")

app = FastAPI(title="Connek · floor")


@app.get("/api/v1/floor/")
def root() -> dict[str, str]:
    return {"service": "floor", "status": "not_implemented"}


# app.include_router(router, prefix="/api/v1")
