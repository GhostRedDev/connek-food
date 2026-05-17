"""Vercel Function placeholder — context: staff.

Cuando implementes este contexto:
1. Crea src/contexts/staff/interface/router.py
2. Importa el router aquí
3. Reemplaza el endpoint placeholder
4. Activa init_sentry
"""
from __future__ import annotations

from fastapi import FastAPI

# from src.shared.telemetry import init_sentry
# from src.contexts.staff.interface.router import router

# init_sentry(service_name="staff")

app = FastAPI(title="Connek · staff")


@app.get("/api/v1/staff/")
def root() -> dict[str, str]:
    return {"service": "staff", "status": "not_implemented"}


# app.include_router(router, prefix="/api/v1")
