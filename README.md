# Connek Restaurant OS

SaaS multi-tenant para restaurantes — reservas, waitlist, floor plan, CRM, comunicación automatizada, reviews con IA.

> **Para IAs/agentes:** lee [CLAUDE.md](CLAUDE.md) en la raíz y el `CLAUDE.md` de cada carpeta antes de tocar código.

## Stack

- **Backend:** FastAPI (Python 3.13) en Clean Architecture, deployado como Vercel Functions (una por bounded context).
- **DB:** Supabase Postgres con Row Level Security.
- **Auth + Realtime + Storage:** Supabase (cliente directo desde Tauri).
- **Frontend:** Tauri 2 + React 19 + TypeScript + shadcn/ui.
- **IA:** OpenAI GPT-4o-mini.
- **Comunicación:** Twilio WhatsApp Sandbox + Resend email.
- **Pagos:** Stripe Billing.
- **Observabilidad:** Sentry.

## Estructura

```
connek-food/
├── backend/      → FastAPI + Clean Architecture
├── desktop/      → Tauri + React + TypeScript
├── supabase/     → SQL migrations, RLS policies
└── shared/       → OpenAPI schema + tipos TS generados
```

Cada carpeta tiene su propio `CLAUDE.md` con reglas estrictas para IAs y devs.

## Quick start

```bash
# Prerequisitos: Node 22+, Python 3.13+, uv, pnpm, supabase CLI, docker

# 1. Clonar y configurar env
cp .env.example .env  # editar con tus keys

# 2. Levantar Supabase local
supabase start

# 3. Backend
cd backend && uv sync
uv run alembic upgrade head
uv run uvicorn src.main_dev:app --reload --port 8000

# 4. Desktop (otra terminal)
cd desktop && pnpm install
pnpm tauri dev

# 5. Generar tipos compartidos
make generate-types
```

Ver `Makefile` para todos los comandos.

## Plan MVP 30 días

Ver memoria de Claude o pregunta al humano.

## Convenciones

- **Commits:** imperativo, sin emoji, sin prefijo convencional.
- **Branches:** `feature/<descripcion>`, `fix/<bug>`, `chore/<tooling>`.
- **PRs:** descripción breve, link al issue/plan, checklist de tests.
