# clients/ — CRM clientes + visitas + historial

> Reglas globales: [/CLAUDE.md](../../../../CLAUDE.md).

## Responsabilidad

Catálogo de comensales del restaurante. Cada vez que llega un cliente (reserva, waitlist, walk-in) se crea/actualiza un `Client`. Historial completo de visitas, preferencias, cumpleaños, notas del staff.

## Entidades

- `Client`: restaurant_id, full_name, phone (único por restaurant), email, birthday, visit_count, last_visit_at, notes, tags (JSONB), opt_in_whatsapp (booleano para Twilio Sandbox).
- `Visit`: client_id, reservation_id (opcional), waitlist_entry_id (opcional), date, spent_amount (manual, opcional), was_no_show.

## Reglas duras

1. **`find_or_create_by_phone(restaurant_id, phone, name?)`** es el use case principal. Llamado por `reservations` y `waitlist` cuando entra un nuevo cliente. **Idempotente.**
2. **`visit_count`** se actualiza en use case `RecordVisitUseCase` cuando una reserva pasa a `completed` o un `WaitlistEntry` pasa a `seated`. **No es trigger SQL** — está en application layer para que la lógica sea explícita.
3. **Phone normalization**: siempre E.164 (`+521234567890`). Validación en `domain/value_objects.py:PhoneNumber` o usa `shared/domain/value_objects.py`.
4. **`opt_in_whatsapp`**: requerido `true` antes de enviar WhatsApp por Twilio Sandbox (compliance + el cliente debe haber escrito el código de opt-in al sandbox).

## Endpoints

- `CRUD /api/v1/clients`
- `GET /api/v1/clients/{id}/history`
- `POST /api/v1/clients/find-or-create` (idempotent, llamado internamente)
- `POST /api/v1/clients/{id}/opt-in-whatsapp` (sets flag + envía link de sandbox)
