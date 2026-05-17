"""Vercel Function placeholder — context: internal_cron.

Cuando implementes este contexto:
1. Crea src/contexts/internal_cron/interface/router.py
2. Importa el router aquí
3. Reemplaza el endpoint placeholder
4. Activa init_sentry
"""
from __future__ import annotations

from fastapi import FastAPI

# from src.shared.telemetry import init_sentry
# from src.contexts.internal_cron.interface.router import router

# init_sentry(service_name="internal_cron")

app = FastAPI(title="Connek · internal_cron")


@app.get("/api/v1/internal_cron/")
def root() -> dict[str, str]:
    return {"service": "internal_cron", "status": "not_implemented"}


# app.include_router(router, prefix="/api/v1")
