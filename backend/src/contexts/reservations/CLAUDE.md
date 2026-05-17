# reservations/ — Reservas + estados + calendar/timeline

> Reglas globales: [/CLAUDE.md](../../../../CLAUDE.md).

## Responsabilidad

Core del producto. CRUD de reservas + state machine + asignación de mesa + filtros + vistas calendar/timeline. Dispara comunicaciones (SMS confirmación, recordatorio) llamando a `communications/` vía HTTP interno.

## Entidades

- `Reservation`: restaurant_id, client_id, party_size, start_at, end_at, table_id (opcional), status, source, notes, occasion, created_by_user_id.
- `ReservationStatus` (enum): `pending`, `confirmed`, `seated`, `completed`, `cancelled`, `no_show`.

## State machine (ENFORCED en domain)

```
pending ──confirm──► confirmed ──seat──► seated ──complete──► completed
   │                     │                  │
   │                     ├──cancel──► cancelled
   │                     └──no_show──► no_show
   └──cancel──► cancelled
```

Transiciones inválidas lanzan `InvalidStateTransition` (de `shared/domain/errors.py`).

## Reglas duras

1. **State machine vive en `domain/entities.py`**, NO en service layer. Método `reservation.seat()` valida y muta.
2. **Validación de overlap de mesa** (no se puede sentar 2 grupos en la misma mesa al mismo tiempo) vive en `application/use_cases.py:AssignTableUseCase`.
3. **Crear reserva = autocrea Client si no existe** (busca por phone). Use case `CreateReservationUseCase` orquesta `clients.find_or_create_by_phone()` → HTTP call al endpoint `/api/v1/clients/find-or-create`.
4. **Completar reserva NO envía la review request directamente.** Solo cambia estado y dispara un row en una tabla `pending_review_requests`. El cron `internal_cron/send-review-requests` se encarga del envío.
5. **Calendar y timeline son queries, no entidades.** Viven en `application/queries.py:GetCalendarQuery` + `GetTimelineQuery`.

## Endpoints

- `CRUD /api/v1/reservations` (filtros: `?date=`, `?status=`, `?client_id=`, `?source=`)
- `GET /api/v1/reservations/calendar?from=&to=&restaurant_id=`
- `GET /api/v1/reservations/timeline?date=&restaurant_id=`
- `POST /api/v1/reservations/{id}/seat` (acción)
- `POST /api/v1/reservations/{id}/no-show`
- `POST /api/v1/reservations/{id}/complete`
- `POST /api/v1/reservations/{id}/cancel`
