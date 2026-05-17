# restaurants/ — Restaurant + Settings + Branding

> Reglas globales: [/CLAUDE.md](../../../../CLAUDE.md).

## Responsabilidad

Modela el restaurante físico que pertenece a una organización. Una org puede tener N restaurantes (cadena). Cada restaurante tiene sus settings (horarios, branding, signature SMS) y FK desde Reservations/Floor/Waitlist/Clients hacia él.

## Entidades

- `Restaurant`: name, timezone, address, phone, logo_url (Supabase Storage), hours (JSONB con horarios por día), org_id.
- `RestaurantSettings`: 1:1 con Restaurant — branding (colors), sms_signature, email_from, ai_enabled, default_party_size, etc.

## Reglas duras

1. **Toda tabla downstream** (reservations, tables, waitlist, clients, reviews) tiene FK a `restaurant_id`, no solo a `organization_id`. Esto permite reportes por sucursal.
2. **Logo del restaurante** se sube a Supabase Storage directo desde Tauri. Este contexto solo guarda la URL.
3. **Horarios** se guardan como JSONB: `{"mon": [{"open": "12:00", "close": "23:00"}], ...}`. Lógica de "está abierto ahora" vive en `domain/services.py`.

## Endpoints

- `CRUD /api/v1/restaurants`
- `GET /api/v1/restaurants/{id}/settings`
- `PATCH /api/v1/restaurants/{id}/settings`
- `GET /api/v1/restaurants/{id}/is-open` — helper para Tauri
