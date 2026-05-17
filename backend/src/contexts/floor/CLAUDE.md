# floor/ — Mesas + FloorPlan + transiciones de estado

> Reglas globales: [/CLAUDE.md](../../../../CLAUDE.md).

## Responsabilidad

Mesas físicas del restaurante con posición visual (x, y, shape) y estado en tiempo real. Tauri se suscribe vía **Supabase Realtime** a esta tabla para que el floor plan en pantalla refleje cambios instantáneamente.

## Entidades

- `Table`: restaurant_id, name (e.g. "Mesa 5"), capacity, x, y, shape (`round`/`square`/`rect`), width, height, status, current_reservation_id (opcional).
- `FloorPlan`: restaurant_id, name ("Patio", "Salón Principal"), layout_json. Una mesa puede pertenecer a un plan.
- `TableStatus` (enum): `available`, `reserved`, `occupied`, `cleaning`.

## Reglas duras

1. **Realtime es Supabase, no SSE/WebSocket de FastAPI.** Tauri usa `supabase.channel('floor_tables').on('postgres_changes', ...)`. Este contexto solo cambia el estado en DB.
2. **Cambio de estado dispara automáticamente Realtime** (Supabase escucha INSERT/UPDATE/DELETE en `floor_tables`). NO hace falta publicar evento manual.
3. **Asignar mesa a reserva** = cambiar `table.status` + setear `table.current_reservation_id`. Si la reserva pasa a `completed`/`cancelled`, otro use case libera la mesa (`status = cleaning`, current_reservation_id = null).
4. **Transición `cleaning → available`** la dispara el staff manualmente en UI (no automático).

## Endpoints

- `CRUD /api/v1/floor/tables`
- `CRUD /api/v1/floor/plans`
- `PATCH /api/v1/floor/tables/{id}/status` (acción explícita con validación de transición)
- `POST /api/v1/floor/tables/{id}/assign` (body: `reservation_id`)
- `POST /api/v1/floor/tables/{id}/release`
