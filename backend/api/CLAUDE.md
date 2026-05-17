# backend/api/ — Entrypoints Vercel Functions

> Reglas en [/CLAUDE.md](../../CLAUDE.md) y [/backend/CLAUDE.md](../CLAUDE.md).

## Propósito

Cada archivo `.py` aquí = **una Vercel Function** = un bounded context expuesto como microservicio independiente.

## Reglas duras

1. **Un archivo por contexto.** Nombre = nombre del contexto. `reservations.py` monta `src/contexts/reservations/interface/router.py`.

2. **El archivo es solo el shell:**
   - Inicia Sentry
   - Crea `FastAPI()` app
   - Monta el router del contexto
   - Configura CORS si Tauri lo consume directo
   - Expone `app` (Vercel lo detecta automáticamente)

3. **NO pongas lógica aquí.** Si algo no encaja en `src/contexts/<x>/interface/`, repensa la arquitectura.

4. **Special files:**
   - `internal_cron.py`: endpoints `/internal/cron/*` llamados por Supabase `pg_net`. Auth = HMAC de `INTERNAL_CRON_SECRET`. NO accesible públicamente.

## Template

```python
# backend/api/<context>.py
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.shared.telemetry import init_sentry
from src.shared.settings import settings
from src.contexts.<context>.interface.router import router

init_sentry(service_name="<context>")

app = FastAPI(
    title=f"Connek · <Context>",
    version="0.1.0",
    docs_url="/docs" if settings.env != "production" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")
```

## Routing en Vercel

`vercel.ts` en raíz mapea `/api/v1/<context>/*` → `backend/api/<context>.py`. NUNCA cambies esto sin actualizar `vercel.ts` Y el router del contexto.
