# identity/ — Users, Organizations, Memberships

> Reglas en [/CLAUDE.md](../../../../CLAUDE.md), [/backend/CLAUDE.md](../../../CLAUDE.md), [/backend/src/contexts/CLAUDE.md](../CLAUDE.md).

## Responsabilidad

Modela quién entra al sistema y a qué organización pertenece. Trabaja **sobre** Supabase Auth (no lo reemplaza).

- Supabase Auth maneja: signup, login, JWT, password reset, OAuth, magic link.
- Este contexto maneja: `Organization`, `Membership`, `Role`, invitaciones, perfil extendido del usuario.

## Entidades clave

- `Organization`: el restaurante o grupo de restaurantes. Tiene `slug`, `name`, `plan` (free/pro), timestamps.
- `Membership`: vincula un `User` (de `auth.users` de Supabase) con una `Organization` y un `Role`.
- `Role`: enum `owner` / `manager` / `host` / `super_admin`. El `super_admin` es interno a Connek (no pertenece a una org de cliente).
- `Invitation`: token + email + role + org → un usuario acepta y se convierte en Membership.

## Reglas duras

1. **No tocar `auth.users`** (es de Supabase). Solo referenciar `user_id uuid` con FK lógica (sin CONSTRAINT cross-schema). Trigger Supabase puede sincronizar metadata.
2. **Crear una Organization SIEMPRE crea un Membership owner** para el user que la creó (use case `CreateOrganizationWithOwnerUseCase`).
3. **`super_admin` no se crea por API.** Se asigna manualmente en DB (`update memberships set role='super_admin'`) o vía script.
4. **JWT de Supabase Auth contiene `sub` (user_id)**, no `organization_id`. La org activa la pasa el frontend en un header `X-Organization-Id` y `shared/auth/tenant.py` la valida contra `memberships`.

## Endpoints

- `POST /api/v1/identity/organizations` — crea org + membership owner.
- `GET /api/v1/identity/me` — perfil + memberships del user actual.
- `POST /api/v1/identity/organizations/{id}/invitations` — invita email a la org.
- `POST /api/v1/identity/invitations/{token}/accept` — acepta invitación.
- `GET /api/v1/identity/organizations/{id}/members` — lista miembros (solo owner/manager).
- `PATCH /api/v1/identity/memberships/{id}` — cambia role (solo owner).
- `DELETE /api/v1/identity/memberships/{id}` — remueve miembro (solo owner).

## Este es el TEMPLATE para clean architecture

Cuando crees un nuevo contexto, copia esta carpeta. Mantén esta estructura limpia y bien documentada — es el modelo a seguir.
