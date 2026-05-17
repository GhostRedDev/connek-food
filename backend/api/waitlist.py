"""Vercel Function placeholder — context: waitlist.

Cuando implementes este contexto:
1. Crea src/contexts/waitlist/interface/router.py
2. Importa el router aquí
3. Reemplaza el endpoint placeholder
4. Activa init_sentry
"""
from __future__ import annotations

from fastapi import FastAPI

# from src.shared.telemetry import init_sentry
# from src.contexts.waitlist.interface.router import router

# init_sentry(service_name="waitlist")

app = FastAPI(title="Connek · waitlist")


@app.get("/api/v1/waitlist/")
def root() -> dict[str, str]:
    return {"service": "waitlist", "status": "not_implemented"}


# app.include_router(router, prefix="/api/v1")
