# waitlist/ — Lista de espera + wait time + notify

> Reglas globales: [/CLAUDE.md](../../../../CLAUDE.md).

## Responsabilidad

Cuando llegan clientes sin reserva, entran a la lista de espera con un tiempo estimado. Cuando una mesa se libera, el staff toca "Notify" y el cliente recibe WhatsApp ("tu mesa está lista").

## Entidades

- `WaitlistEntry`: restaurant_id, client_id (autocreate por phone), party_size, quoted_wait_minutes, status, notified_at, seated_at, position_in_queue.
- `WaitlistStatus` (enum): `waiting`, `notified`, `seated`, `left` (se fue sin esperar).

## Reglas duras

1. **Cálculo de `quoted_wait_minutes`** vive en `domain/services.py:WaitTimeCalculator`. Heurística MVP simple: `(personas_delante_con_party_size_similar * tiempo_promedio_mesa)`. Mejorable post-MVP.
2. **Notify dispara WhatsApp**: use case `NotifyWaitlistEntryUseCase` cambia estado → `notified` Y llama vía HTTP a `/api/v1/communications/send` con template `waitlist_ready`.
3. **Realtime via Supabase**: Tauri se suscribe a la tabla `waitlist_entries` para actualizar la cola en vivo.
4. **Auto-expiración**: cron `internal_cron/cleanup-waitlist` cada 30min marca como `left` entradas `notified` hace >30min sin `seated`.

## Endpoints

- `CRUD /api/v1/waitlist`
- `GET /api/v1/waitlist/wait-estimate?party_size=&restaurant_id=` (sin crear entry)
- `POST /api/v1/waitlist/{id}/notify` (dispara WhatsApp)
- `POST /api/v1/waitlist/{id}/seat` (transición a `seated`, libera de cola)
