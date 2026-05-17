"""Vercel Function placeholder — context: restaurants.

Cuando implementes este contexto:
1. Crea src/contexts/restaurants/interface/router.py
2. Importa el router aquí
3. Reemplaza el endpoint placeholder
4. Activa init_sentry
"""
from __future__ import annotations

from fastapi import FastAPI

# from src.shared.telemetry import init_sentry
# from src.contexts.restaurants.interface.router import router

# init_sentry(service_name="restaurants")

app = FastAPI(title="Connek · restaurants")


@app.get("/api/v1/restaurants/")
def root() -> dict[str, str]:
    return {"service": "restaurants", "status": "not_implemented"}


# app.include_router(router, prefix="/api/v1")
