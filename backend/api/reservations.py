"""Vercel Function placeholder — context: reservations.

Cuando implementes este contexto:
1. Crea src/contexts/reservations/interface/router.py
2. Importa el router aquí
3. Reemplaza el endpoint placeholder
4. Activa init_sentry
"""
from __future__ import annotations

from fastapi import FastAPI

# from src.shared.telemetry import init_sentry
# from src.contexts.reservations.interface.router import router

# init_sentry(service_name="reservations")

app = FastAPI(title="Connek · reservations")


@app.get("/api/v1/reservations/")
def root() -> dict[str, str]:
    return {"service": "reservations", "status": "not_implemented"}


# app.include_router(router, prefix="/api/v1")
