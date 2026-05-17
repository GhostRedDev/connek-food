# backend/alembic/ — Migraciones de schema (SQLAlchemy)

> Reglas en [/CLAUDE.md](../../CLAUDE.md).

## Qué vive aquí

Migraciones de **estructura de tablas** que SQLAlchemy maneja. Generadas con `alembic revision --autogenerate`.

## Qué NO vive aquí

- RLS policies → `supabase/migrations/`
- Triggers Postgres → `supabase/migrations/`
- pg_cron jobs → `supabase/migrations/`
- Seeds → `backend/scripts/seed_demo.py` o `supabase/seed.sql`

Razón: Alembic genera SQL agnóstico; las features Postgres-específicas (RLS, pg_cron, pg_net) viven en SQL puro en Supabase para que el equipo las vea como código de Supabase, no como infraestructura de Python.

## Reglas duras

1. **Nunca edites una migración mergeada.** Crea una nueva.
2. **Nombres descriptivos:** `add_reservations_table`, `add_status_to_floor_tables`. No `change` ni `fix`.
3. **Revisa el SQL autogenerado** antes de commit. Alembic se equivoca con tipos custom y RLS.
4. **Sin downgrades a producción.** Implementa `downgrade()` pero asume que no se usa.
5. **Una sola cabeza siempre.** Si CI marca multiple heads, mergea antes de continuar.

## Comandos

```bash
uv run alembic revision --autogenerate -m "add reservations table"
uv run alembic upgrade head
uv run alembic downgrade -1   # solo dev local
uv run alembic history
uv run alembic current
```
