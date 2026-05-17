"""Vercel Function placeholder — context: admin.

Cuando implementes este contexto:
1. Crea src/contexts/admin/interface/router.py
2. Importa el router aquí
3. Reemplaza el endpoint placeholder
4. Activa init_sentry
"""
from __future__ import annotations

from fastapi import FastAPI

# from src.shared.telemetry import init_sentry
# from src.contexts.admin.interface.router import router

# init_sentry(service_name="admin")

app = FastAPI(title="Connek · admin")


@app.get("/api/v1/admin/")
def root() -> dict[str, str]:
    return {"service": "admin", "status": "not_implemented"}


# app.include_router(router, prefix="/api/v1")
