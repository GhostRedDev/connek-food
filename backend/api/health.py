"""Health check function — sin dependencias del proyecto, validar deploy Vercel."""
from __future__ import annotations

import os
from datetime import datetime, timezone

from fastapi import FastAPI

app = FastAPI(title="Connek · Health", docs_url=None, redoc_url=None)


@app.get("/api/v1/health")
def health() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "service": "health",
        "env": os.getenv("VERCEL_ENV", "local"),
        "commit": os.getenv("VERCEL_GIT_COMMIT_SHA", "unknown")[:7],
        "region": os.getenv("VERCEL_REGION", "unknown"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/v1/health/ready")
def ready() -> dict[str, bool]:
    return {"ready": True}
