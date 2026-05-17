# supabase/ — Migraciones, RLS, Edge Functions

> Reglas globales: [/CLAUDE.md](../CLAUDE.md).

## Propósito

Todo lo que vive **dentro de Supabase**: SQL migrations (RLS policies, triggers, índices), Edge Functions (Deno, opcional), seed data, configuración del proyecto.

## Estructura

```
supabase/
├── config.toml            # supabase CLI config
├── migrations/            # SQL puro (ordenado por timestamp)
│   ├── 20260517000000_initial_schema.sql
│   ├── 20260517000100_rls_policies.sql
│   ├── 20260517000200_helper_functions.sql
│   └── 20260517000300_pg_cron_jobs.sql
├── seed.sql               # datos iniciales para `supabase db reset`
└── functions/             # Edge Functions Deno (opcional)
    └── <function_name>/
        └── index.ts
```

## División de responsabilidades

| Qué | Dónde |
|---|---|
| Crear tablas, columnas, FKs, índices | `backend/alembic/` (Alembic) |
| RLS policies | `supabase/migrations/` |
| Triggers Postgres | `supabase/migrations/` |
| Helper functions SQL (`current_org_id()`, etc.) | `supabase/migrations/` |
| `pg_cron` jobs | `supabase/migrations/` |
| Edge Functions Deno | `supabase/functions/` |
| Seed data inicial | `supabase/seed.sql` |
| Demo data (post-setup) | `backend/scripts/seed_demo.py` |

**Justificación**: Alembic genera SQL agnóstico de Postgres y se prestaría mal para RLS/triggers/pg_cron. Las features Postgres-específicas van en SQL puro versionado en `supabase/migrations/` para que el equipo las vea como "código Supabase" y no como infra Python.

## Reglas duras

1. **TODA tabla con datos de restaurante DEBE tener:**
   - Columna `organization_id uuid not null references organizations(id) on delete cascade`
   - `alter table <x> enable row level security;`
   - 4 policies: select / insert / update / delete (template en `supabase/migrations/_rls_template.sql`)
   - Índice en `organization_id`

2. **Las policies usan `auth.uid()`** (función nativa de Supabase Auth) cruzada con `memberships`:
   ```sql
   create policy "members read their org data"
   on <table> for select
   to authenticated
   using (organization_id in (
     select organization_id from memberships where user_id = auth.uid()
   ));
   ```

3. **NO `drop table` ni `drop column` en migraciones de producción.** Renombra a `_deprecated_` y elimina en una segunda migración semanas después.

4. **pg_cron jobs llaman FastAPI via `pg_net`:**
   ```sql
   select cron.schedule(
     'send-reminders',
     '*/5 * * * *',
     $$
     select net.http_post(
       url := 'https://api.connek.ca/internal/cron/send-reminders',
       headers := jsonb_build_object('Authorization', 'Bearer ' || current_setting('app.internal_cron_secret'))
     );
     $$
   );
   ```
   El secret se setea con `alter database postgres set "app.internal_cron_secret" = '...';` (NO en SQL versionado).

5. **Edge Functions son opcionales** y solo para casos específicos (e.g. webhooks que necesitan latencia muy baja). Default: FastAPI.

6. **Naming convention de migraciones:**
   - `YYYYMMDDHHMMSS_<descripcion_kebab>.sql`
   - Una sola operación lógica por migración.

## Comandos

```bash
# Setup local
supabase init                           # primera vez (ya hecho)
supabase start                          # levanta Postgres + Auth + Realtime + Studio locales
supabase status                         # ver URLs y keys locales
supabase stop

# Migraciones
supabase migration new <descripcion>    # crea archivo timestamped
supabase db reset                       # resetea local y aplica migraciones + seed
supabase db push                        # aplica al proyecto remoto (cuidado!)
supabase db diff -f <name>              # diff desde local → genera migración

# Edge Functions
supabase functions new <name>
supabase functions serve <name>
supabase functions deploy <name>
```

## Anti-patrones

- ❌ Tabla sin RLS habilitado.
- ❌ Policy genérica `using (true)` o `using (auth.role() = 'authenticated')` — debe filtrar por org.
- ❌ Service-role usado desde frontend.
- ❌ Trigger que llama a un endpoint HTTP externo (usa pg_cron → endpoint, no triggers).
- ❌ Edge Function que reimplementa lo que FastAPI ya tiene.
