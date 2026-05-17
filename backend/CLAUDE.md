# backend/ — FastAPI + Clean Architecture

> Reglas globales en [/CLAUDE.md](../CLAUDE.md). Este archivo manda dentro de `backend/`.

## Propósito

Backend Python que sirve la lógica de negocio que Supabase no cubre (IA, WhatsApp, Stripe, validaciones complejas, jobs). Auth, realtime, storage y CRUD simple van directo de Tauri a Supabase — no aquí.

## Tooling

- **Runtime:** Python 3.13.
- **Package manager:** `uv` (no pip, no poetry). Comandos: `uv add <pkg>`, `uv sync`, `uv run <cmd>`.
- **Format/lint:** `ruff format` + `ruff check`. Line length 100.
- **Typecheck:** `mypy` (strict opcional, type hints obligatorios en código nuevo).
- **Tests:** `pytest` + `pytest-asyncio` + `factory_boy`. Mínimo 70% cobertura, dominio 100%.

## Estructura

```
backend/
├── pyproject.toml          # uv + dependencias + ruff + mypy + pytest config
├── alembic.ini             # config Alembic
├── alembic/                # migraciones SQLAlchemy
│   └── versions/
├── api/                    # entrypoints Vercel (1 por bounded context)
│   ├── identity.py
│   ├── reservations.py
│   └── ...                 # uno por contexto en src/contexts/
├── src/
│   ├── shared/             # shared kernel — usado por todos los contexts
│   │   ├── auth/           # JWT validation, TenantContext, DI dependencies
│   │   ├── db/             # SQLAlchemy session factory, base models
│   │   ├── domain/         # ValueObjects base, errores de dominio
│   │   ├── errors.py       # excepciones HTTP mapeadas
│   │   ├── pagination.py
│   │   ├── settings.py     # pydantic-settings
│   │   └── telemetry.py    # Sentry + structured logging
│   ├── contexts/           # bounded contexts — cada uno es independiente
│   │   ├── identity/
│   │   ├── restaurants/
│   │   ├── reservations/
│   │   ├── floor/
│   │   ├── waitlist/
│   │   ├── clients/
│   │   ├── communications/
│   │   ├── reviews/
│   │   ├── ai/
│   │   ├── staff/
│   │   ├── billing/
│   │   └── admin/
│   └── factories/          # factory_boy factories (compartidas entre tests)
├── tests/
│   ├── conftest.py
│   ├── unit/               # dominio + application (sin DB, sin red)
│   ├── integration/        # con Supabase local (RLS verificado)
│   └── e2e/                # flujos golden path completos
└── scripts/
    └── seed_demo.py
```

## Reglas duras

1. **Cada bounded context es un mini-microservicio.**
   - Una sola Vercel Function en `api/<context>.py`.
   - Sin imports entre contextos (`from src.contexts.X` dentro de `src.contexts.Y` → PROHIBIDO).
   - Comparten DB pero no código de dominio.

2. **Capas Clean Arch (re-confirmando lo de /CLAUDE.md):**
   - `domain/`: entidades, value objects, interfaces (Protocols), business rules, errores de dominio. **CERO imports de framework.**
   - `application/`: use cases (= command/query handlers). Orquesta `domain/` y servicios inyectados.
   - `infrastructure/`: implementa Protocols del dominio. Aquí van SQLAlchemy repos, adapters Supabase/Twilio/OpenAI/Stripe.
   - `interface/`: routers FastAPI, DTOs Pydantic, dependencies para DI.

3. **DI con `Depends()` de FastAPI.** Las factories `get_<thing>` viven en `<context>/interface/dependencies.py`.

4. **DB access via SQLAlchemy 2.x async + JWT del user.** El cliente Postgres usa el JWT del usuario autenticado para que RLS aplique. Excepciones (service-role): `contexts/admin/` y `api/internal_cron.py`.

5. **Migraciones con Alembic** para schema. RLS policies van en `supabase/migrations/` (SQL puro).

6. **Errores:** lanza excepciones de dominio en `domain/`/`application/`. Mapeo a HTTP en `src/shared/errors.py` (exception_handler global).

7. **Logging:** structured (JSON). Sentry capturea excepciones unhandled automáticamente. No `print()`.

## Comandos comunes

```bash
# Setup
cd backend && uv sync

# Dev server local (todos los contexts en un solo proceso, modo dev)
uv run uvicorn src.main_dev:app --reload --port 8000

# Tests
uv run pytest                        # todos
uv run pytest tests/unit            # solo unit
uv run pytest -k tenancy            # filtrar
uv run pytest --cov=src --cov-report=term-missing

# Lint + typecheck
uv run ruff format .
uv run ruff check . --fix
uv run mypy src

# Migrations
uv run alembic revision --autogenerate -m "add reservations table"
uv run alembic upgrade head

# OpenAPI export (para shared/types.ts)
uv run python scripts/export_openapi.py > ../shared/openapi.json
```

## Cuando crees un nuevo contexto

Sigue este orden estricto:
1. Copia la estructura de `src/contexts/identity/` como template.
2. Implementa **domain primero**: entidades, value objects, repository Protocols, errores.
3. Tests unit del dominio (state machines, business rules).
4. **application**: use cases que orquestan dominio + servicios.
5. Tests unit de application (con mocks de los Protocols).
6. **infrastructure**: repos SQLAlchemy, adapters externos.
7. Tests integration (DB real, RLS).
8. **interface**: routers + DTOs + dependencies.
9. Tests E2E del happy path.
10. Crear `api/<context>.py` que monta el router e inicia Sentry.
11. Agregar entry en `vercel.ts` + rewrite en root.

## Anti-patrones (NO HAGAS)

- ❌ `from fastapi import ...` en cualquier archivo de `domain/`.
- ❌ Query con `.where(table.organization_id == ...)` — RLS lo hace.
- ❌ Llamar `os.environ['X']` — usa `settings.X`.
- ❌ Manejar auth/realtime/storage desde el backend cuando Tauri ya tiene Supabase.
- ❌ Imports entre contextos (`from src.contexts.X` dentro de Y).
- ❌ Mocks en tests integration (usa Supabase local).
- ❌ Lógica de negocio en routers (`interface/`).
- ❌ SQL crudo en `application/` o `domain/`.
