# backend/src/shared/ — Shared Kernel

> Reglas en [/CLAUDE.md](../../../CLAUDE.md) y [/backend/CLAUDE.md](../../CLAUDE.md).

## Propósito

Código que cruza bounded contexts: auth, DB session, errores, paginación, telemetría, settings. Antes de duplicar algo en un contexto, **mira aquí primero**.

## Estructura

```
shared/
├── __init__.py
├── auth/                 # JWT de Supabase, TenantContext, DI dependencies
│   ├── __init__.py
│   ├── jwt.py           # decode + validate Supabase JWT
│   ├── tenant.py        # TenantContext dataclass
│   └── dependencies.py  # require_user, require_tenant, require_role
├── db/                   # SQLAlchemy session factory
│   ├── __init__.py
│   ├── base.py          # declarative_base + naming convention
│   ├── session.py       # async_session_maker (con JWT del user)
│   └── service_session.py # async_session_maker (service-role, solo admin/cron)
├── domain/               # base classes y value objects compartidos
│   ├── __init__.py
│   ├── value_objects.py # PhoneNumber, Email, Money, etc.
│   ├── ids.py           # UUID-based ID types
│   └── errors.py        # DomainError, InvalidStateTransition, etc.
├── errors.py             # HTTP exception handlers (mapea DomainError → HTTP)
├── pagination.py         # cursor-based pagination utilities
├── settings.py           # pydantic-settings — TODA env var pasa por aquí
└── telemetry.py          # Sentry init + structured logger
```

## Reglas duras

1. **`shared/domain/` sigue las reglas Clean Arch del nivel raíz.** Cero imports de FastAPI/SQLAlchemy/Supabase.

2. **`shared/auth/`** es el ÚNICO lugar que valida JWT de Supabase. Si un contexto inventa su propia validación, está mal.

3. **`shared/db/session.py`** retorna sesión SQLAlchemy con el JWT del usuario inyectado en la conexión Postgres → RLS aplica. Para excepciones (admin/cron), usa `service_session.py` y deja un comentario `# RLS bypass: motivo`.

4. **`shared/settings.py`** es la ÚNICA puerta a variables de entorno. Cualquier `os.environ['X']` fuera de aquí → bug.

5. **`shared/errors.py`** define `register_exception_handlers(app)` que mapea:
   - `DomainError` → 400
   - `NotFoundError` → 404
   - `ForbiddenError` → 403
   - `InvalidStateTransition` → 409
   - Excepciones unhandled → Sentry + 500

6. **`shared/telemetry.py`** expone `init_sentry(service_name)` que se llama en cada `api/<context>.py`.

7. **No agregues helpers genéricos aquí sin justificar.** Si solo lo usa 1 contexto, vive en ese contexto. Aquí solo lo que usan **2 o más**.

## Crecimiento

Cuando un patrón se repite en 2+ contextos, **extráelo aquí**. No esperes el tercero. Lecto-escritura desde código: rápido. Refactor cross-context: caro.
