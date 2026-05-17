# staff/ — Staff members + shifts

> Reglas globales: [/CLAUDE.md](../../../../CLAUDE.md).

## Responsabilidad

Lista de empleados del restaurante con sus turnos (shifts). MVP simple: CRUD + visualización de turnos. No payroll, no time-tracking (post-MVP).

## Entidades

- `StaffMember`: restaurant_id, user_id (opcional, si tiene cuenta en el sistema), name, role (host/server/manager/cook), phone, email, hired_at, is_active.
- `Shift`: staff_member_id, start_at, end_at, position (host/server/bar).

## Reglas duras

1. **`user_id` opcional**: un staff member puede existir sin tener login (lo crea el owner manualmente). Si tiene `user_id`, hereda permisos del Membership.
2. **Sin solapamiento de shifts**: validación en `application/use_cases.py:CreateShiftUseCase` rechaza si el staff_member ya tiene shift en ese rango.
3. **No es para autoasignación**: los shifts los crea el manager/owner. Los staff solo los ven.

## Endpoints

- `CRUD /api/v1/staff`
- `CRUD /api/v1/staff/shifts`
- `GET /api/v1/staff/shifts/today?restaurant_id=`
