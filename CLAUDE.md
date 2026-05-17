# Connek Restaurant OS — Reglas globales para IAs

> Este archivo es **órdenes estrictas**. Toda IA (Claude, Cursor, Copilot, etc.) que trabaje en este repo DEBE leerlo y respetarlo. Antes de editar cualquier archivo, lee también el `CLAUDE.md` de la carpeta correspondiente.

## Qué estamos construyendo

Connek Restaurant OS — SaaS multi-tenant para restaurantes (competencia: SevenRooms, OpenTable, Libro). Objetivo: **MVP vendible en 30 días**, no producto perfecto.

Prioridades en este orden: **(1) demo value · (2) velocidad de dev · (3) UX premium · (4) simpleza**. NUNCA arquitectura sobre-ingeniada.

## Stack lockeado — NO se relitiga

| Capa | Tecnología |
|---|---|
| Backend | FastAPI 0.115+ (Python 3.13) |
| Arquitectura | Clean Architecture + modular monolith (1 Vercel Function por bounded context) |
| DB | Supabase Postgres + Row Level Security (RLS) |
| ORM | SQLAlchemy 2.x async + Alembic |
| Auth | Supabase Auth (JWT) |
| Realtime | Supabase Realtime (cliente directo desde Tauri) |
| Storage | Supabase Storage (cliente directo desde Tauri) |
| Background | Supabase pg_cron + pg_net → FastAPI internal endpoints |
| Email | Resend (free tier) |
| WhatsApp/SMS | Twilio WhatsApp Sandbox + modo "fake" para dev/demo |
| IA | OpenAI GPT-4o-mini |
| Pagos | Stripe Billing |
| Observabilidad | Sentry (free tier) |
| Frontend | Tauri 2 + React 19 + TypeScript + shadcn/ui + Tailwind |
| Deploy | Vercel Functions Python 3.13 (Fluid Compute) |
| Monorepo | `backend/` `desktop/` `supabase/` `shared/` |
| Testing | pytest + pytest-asyncio + factory_boy + httpx + vitest |
| Tooling | uv (Python), pnpm (JS) |

Si una tarea parece requerir cambiar el stack, DETENTE y pregunta al humano.

## Reglas duras (rompe una, rompiste todo)

### 1. Clean Architecture — direccionalidad de dependencias

```
interface  ──►  application  ──►  domain
                                     ▲
infrastructure  ─────────────────────┘
```

- `domain/` **NUNCA** importa de `application/`, `infrastructure/`, ni `interface/`. Cero imports de FastAPI, SQLAlchemy, Supabase, OpenAI, Twilio, Stripe, etc.
- `application/` **SOLO** importa de `domain/` (su propio contexto) y de `shared/domain/`.
- `infrastructure/` implementa interfaces (Protocols) definidas en `domain/`. Aquí viven los adapters de Supabase, OpenAI, Twilio, Stripe.
- `interface/` orquesta: parsea HTTP → DTO → command → use case → entity → DTO → HTTP. Conoce a `application/` pero no a `infrastructure/` (todo se inyecta vía DI).

Si tu IDE/AI te sugiere `from src.contexts.X.infrastructure...` dentro de un archivo de `domain/`, es un bug. Detente.

### 2. Multi-tenancy — RLS es la verdad

- **Toda tabla con datos de restaurante DEBE tener `organization_id uuid not null`** + RLS policies.
- FastAPI conecta a Postgres usando el **JWT del usuario** (no service-role). Las policies RLS hacen el filtrado automáticamente.
- Excepciones (service-role permitido): SOLO `contexts/admin/` (super_admin) y `api/internal_cron.py`.
- NUNCA escribas un `.where(Reservation.organization_id == ...)` manual en queries — RLS lo hace.

### 3. Tauri ↔ Supabase ↔ FastAPI — quién habla con quién

- **Tauri ↔ Supabase directo**: auth (login/signup), realtime (subscribe a tablas), storage (upload/download). Usa `supabase-js`.
- **Tauri ↔ FastAPI**: lógica de negocio compleja, IA, WhatsApp, Stripe, acciones que requieren validación server-side. Usa cliente OpenAPI tipado en `shared/types.ts`.
- **FastAPI ↔ Supabase**: lee/escribe DB con JWT del user. Para crons / admin usa service-role.

NUNCA hagas auth/storage/realtime pasando por FastAPI cuando Supabase ya lo da.

### 4. Reuso — antes de crear, busca

Antes de crear cualquier helper, busca en:
1. `backend/src/shared/` — pagination, errors, auth, db session, telemetry, settings
2. `desktop/src/components/` — UI compartida (shadcn/ui ya configurado)
3. `desktop/src/lib/` — clientes (`supabase.ts`, `api.ts`)
4. `shared/types.ts` — tipos generados de OpenAPI

Si encuentras algo similar pero no idéntico, **extiende lo existente**. No dupliques.

### 5. Microservicios pragmáticos

- Cada bounded context (`src/contexts/<name>/`) se empaqueta como **una Vercel Function independiente** en `backend/api/<name>.py`.
- Comparten DB (Supabase) pero NO comparten código de dominio entre contexts. Si dos contexts necesitan algo, va a `shared/`.
- Comunicación entre contexts: vía DB (eventos en tabla, triggers Postgres) o llamadas HTTP. NUNCA imports cruzados (`from src.contexts.X` desde `src.contexts.Y`).

### 6. Sin comentarios obvios, sin dead code, sin TODOs sin owner

- Código auto-documentado por nombres. Comentarios solo para el **PORQUÉ no obvio** (invariantes, workarounds, decisiones contraintuitivas).
- No dejes `# TODO` sin ticket. Si es importante, abre issue.
- No dejes código comentado "por si acaso". Git lo recuerda.

### 7. Tests son obligatorios para flujos críticos

- Antes de mergear: ruff verde + mypy verde + pytest verde.
- Cobertura objetivo 70%. Dominio (state machines, business rules) debe estar al 100%.
- Test bloqueante: `backend/tests/integration/test_tenancy.py` — aislamiento RLS entre orgs.

### 8. Secretos y variables de entorno

- NUNCA commits secretos. `.env` está en `.gitignore`.
- Variables nuevas → agregar a `.env.example` con descripción.
- Usa `src/shared/settings.py` (pydantic-settings) para acceder a variables. NO `os.environ` directo.

### 9. Estilo

- Python: `ruff format` + `ruff check` (line length 100). Type hints en TODO. `from __future__ import annotations` arriba.
- TypeScript: `prettier` + `tsc --strict`. Sin `any`.
- Commits: imperativo presente ("add reservation seat action"), sin emojis, sin "feat:/fix:" si el repo no usa convencionales.

### 10. Cuándo preguntar al humano

- Cambio de stack o arquitectura.
- Decisión que afecta >2 contextos.
- Algo que tomaría >1 día.
- Cualquier ambigüedad de producto (qué debe hacer el restaurante).

## Estructura del repo

```
connek-food/
├── backend/      → FastAPI + Clean Architecture (Python)
├── desktop/      → Tauri + React + TypeScript
├── supabase/     → SQL migrations, RLS policies, Edge Functions
└── shared/       → OpenAPI schema + tipos TypeScript generados
```

Cada subcarpeta tiene su propio `CLAUDE.md` con reglas específicas. Léelo.

## Plan completo

Plan v2 con día a día: ver memoria de Claude (`memory/MEMORY.md`) o pregunta al humano.

## Glosario

- **Tenant / Organization**: un restaurante (o grupo de restaurantes que comparten cuenta).
- **Context / Bounded context**: módulo de dominio (reservations, waitlist, etc.).
- **Use case**: acción de negocio (CreateReservation, NotifyWaitlist, etc.).
- **Entity**: objeto con identidad y ciclo de vida (Reservation, Client, etc.).
- **Value object**: dato inmutable sin identidad (Money, PhoneNumber, etc.).
- **DTO**: estructura de transporte (input/output HTTP). Pydantic.
- **Adapter**: implementación concreta de una interface del dominio (e.g. `SupabaseReservationRepo`).
