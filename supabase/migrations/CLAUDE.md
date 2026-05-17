# supabase/migrations/ — SQL migrations versionados

> Reglas globales: [/CLAUDE.md](../../CLAUDE.md), [/supabase/CLAUDE.md](../CLAUDE.md).

## Qué va aquí

- RLS policies (alter table ... enable row level security + create policy)
- Triggers Postgres
- Helper SQL functions (`current_org_id()`, `current_user_has_role(...)`, etc.)
- pg_cron jobs
- Índices Postgres específicos (full-text search, GIN, BRIN)
- Extensiones (`create extension if not exists pg_cron;`)

## Qué NO va aquí

- Tablas (van en `backend/alembic/`)
- Datos seed (van en `seed.sql` o `backend/scripts/seed_demo.py`)
- Datos de prueba (van en factories de pytest)

## Reglas duras

1. **Una migración = un cambio lógico.** No mezclar policies de tabla A con triggers de tabla B.
2. **SIEMPRE idempotente cuando es posible:**
   ```sql
   create extension if not exists pg_cron;
   create or replace function ...
   drop policy if exists "..." on table; create policy "..." ...
   ```
3. **Naming:** `YYYYMMDDHHMMSS_<descripcion>.sql` (timestamp completo, no fecha sola).
4. **Comentario al principio del archivo:**
   ```sql
   -- Purpose: enable RLS on reservations and add member-scoped policies
   -- Depends on: 20260517000000_initial_schema (memberships table)
   ```
5. **NUNCA borres una migración mergeada.** Crea una nueva que revierta.

## Template: RLS para tabla nueva

```sql
-- 20260520000000_rls_<table>.sql
alter table <table> enable row level security;

create policy "members read <table> of their orgs"
on <table> for select
to authenticated
using (
  organization_id in (
    select organization_id from memberships where user_id = auth.uid()
  )
);

create policy "members insert <table> in their orgs"
on <table> for insert
to authenticated
with check (
  organization_id in (
    select organization_id from memberships where user_id = auth.uid()
  )
);

create policy "managers+ update <table> in their orgs"
on <table> for update
to authenticated
using (
  organization_id in (
    select organization_id from memberships
    where user_id = auth.uid() and role in ('owner', 'manager')
  )
);

create policy "owners delete <table> in their orgs"
on <table> for delete
to authenticated
using (
  organization_id in (
    select organization_id from memberships
    where user_id = auth.uid() and role = 'owner'
  )
);
```
