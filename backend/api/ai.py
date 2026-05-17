"""Vercel Function placeholder — context: ai.

Cuando implementes este contexto:
1. Crea src/contexts/ai/interface/router.py
2. Importa el router aquí
3. Reemplaza el endpoint placeholder
4. Activa init_sentry
"""
from __future__ import annotations

from fastapi import FastAPI

# from src.shared.telemetry import init_sentry
# from src.contexts.ai.interface.router import router

# init_sentry(service_name="ai")

app = FastAPI(title="Connek · ai")


@app.get("/api/v1/ai/")
def root() -> dict[str, str]:
    return {"service": "ai", "status": "not_implemented"}


# app.include_router(router, prefix="/api/v1")
