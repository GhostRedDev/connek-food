# admin/ — Super-admin (bypass tenant)

> Reglas globales: [/CLAUDE.md](../../../../CLAUDE.md).
>
> ⚠️ **CONTEXTO PRIVILEGIADO**: bypass de RLS. Tratar con extremo cuidado.

## Responsabilidad

Vistas internas para el equipo Connek (no para restaurantes clientes). Lista de todas las orgs, todos los usuarios, métricas globales, herramientas de soporte (impersonate user).

## Acceso

- **Solo `Membership.role == 'super_admin'`**. La dependency `require_super_admin` lo enforza.
- Usa **service-role key de Supabase** para queries (bypass RLS). Sesión via `shared/db/service_session.py`.
- Cada endpoint deja audit log en `super_admin_actions` (quién, qué, cuándo, sobre qué org).

## Reglas duras

1. **NO exponer este contexto a clientes**. CORS más restrictivo (solo dominio interno admin.connek.ca, si lo hay).
2. **TODA acción es auditada** vía middleware en `interface/router.py`. Loggea: user_id, endpoint, payload, target_org_id, timestamp.
3. **Impersonate** genera un JWT con `act_as=target_user_id` claim. Tauri lo detecta y muestra banner rojo "Impersonating X — return to admin". JWT expira en 1h.
4. **DELETE es soft-delete** vía `is_archived=true`. NUNCA `DELETE FROM` real en este contexto.
5. **Sin write masivo** (no `update all orgs set ...`). Operaciones de mantenimiento masivo van por scripts en `backend/scripts/`.

## Endpoints

- `GET /api/v1/admin/orgs` (lista con métricas: # restaurants, # users, plan, MRR, last_active_at)
- `GET /api/v1/admin/orgs/{id}` (detalle)
- `GET /api/v1/admin/users`
- `POST /api/v1/admin/impersonate` (body: `user_id` → returns short-lived JWT)
- `POST /api/v1/admin/orgs/{id}/archive` (soft-delete)
- `GET /api/v1/admin/metrics/global` (MRR, # reservations este mes, # SMS, etc.)
- `GET /api/v1/admin/audit-log`
