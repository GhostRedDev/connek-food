"""Vercel Function placeholder — context: reviews.

Cuando implementes este contexto:
1. Crea src/contexts/reviews/interface/router.py
2. Importa el router aquí
3. Reemplaza el endpoint placeholder
4. Activa init_sentry
"""
from __future__ import annotations

from fastapi import FastAPI

# from src.shared.telemetry import init_sentry
# from src.contexts.reviews.interface.router import router

# init_sentry(service_name="reviews")

app = FastAPI(title="Connek · reviews")


@app.get("/api/v1/reviews/")
def root() -> dict[str, str]:
    return {"service": "reviews", "status": "not_implemented"}


# app.include_router(router, prefix="/api/v1")
