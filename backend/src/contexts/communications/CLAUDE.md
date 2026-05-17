# communications/ — Templates + envío SMS/email + logs

> Reglas globales: [/CLAUDE.md](../../../../CLAUDE.md).

## Responsabilidad

Hub centralizado de comunicación con clientes. Templates editables por el restaurante. Adapters para WhatsApp (Twilio Sandbox) y Email (Resend). Logs de todo envío para auditoría y debugging.

## Entidades

- `MessageTemplate`: restaurant_id, kind (`whatsapp`/`email`), trigger (`confirmation`/`reminder`/`waitlist_ready`/`review_request`/`custom`), subject (email), body (Jinja-like vars: `{{client.full_name}}`, `{{reservation.start_at}}`), enabled.
- `MessageLog`: restaurant_id, kind, trigger, to (phone/email), body_rendered, status (`queued`/`sent`/`delivered`/`failed`), provider_id (Twilio SID / Resend ID), error, sent_at, delivered_at, client_id (opcional).

## Adapters (infrastructure/)

- `TwilioWhatsAppAdapter`: usa Twilio Python SDK contra sandbox (`whatsapp:+14155238886`). Maneja opt-in check.
- `ResendEmailAdapter`: usa `resend` Python SDK.
- `FakeMessageAdapter`: cuando `FAKE_SMS_MODE=true`, no envía nada, solo loggea en `MessageLog` con status `sent` y marca `is_fake=true`. Tauri admin UI muestra los fake.

El use case `SendMessageUseCase` recibe un `MessageProvider` por DI según `kind` y `FAKE_SMS_MODE`.

## Reglas duras

1. **TODO envío crea un `MessageLog`** antes de hablar con el provider. Status inicial = `queued`. Update después del provider.
2. **Rendering de template** vive en `domain/services.py:TemplateRenderer` (Jinja2 sandboxed). Recibe `template` + dict de variables. NUNCA permitir código arbitrario.
3. **Opt-in check para WhatsApp** lo hace `TwilioWhatsAppAdapter` antes de enviar. Si client.opt_in_whatsapp=false, marca log como `failed` con error `not_opted_in`.
4. **Webhook de Twilio** (`/api/v1/communications/twilio/webhook`) actualiza `MessageLog.status` y `delivered_at`. Verifica firma HMAC de Twilio.
5. **Rate limiting**: Resend free = 100/día. Si se excede, marca `MessageLog` como `failed` con `rate_limited`. NUNCA hacer reintentos infinitos.

## Endpoints

- `CRUD /api/v1/communications/templates`
- `GET /api/v1/communications/logs` (filtros: status, kind, trigger, date range)
- `POST /api/v1/communications/send` (llamado por otros contextos — body: `template_trigger`, `to`, `variables`)
- `POST /api/v1/communications/send-test` (testing manual desde admin)
- `POST /api/v1/communications/twilio/webhook` (callback Twilio)
- `POST /api/v1/communications/resend/webhook` (callback Resend)
