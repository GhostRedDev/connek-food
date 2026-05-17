# reviews/ — Reviews + token público + AI responses

> Reglas globales: [/CLAUDE.md](../../../../CLAUDE.md).

## Responsabilidad

Post-visita, el cliente recibe un WhatsApp con link único firmado (HMAC) que abre formulario público de review (sin auth). Restaurante ve reviews en su dashboard. IA genera respuesta sugerida que el restaurante puede aprobar o editar.

## Entidades

- `Review`: restaurant_id, client_id, reservation_id (opcional), rating (1-5), comment, public_token (HMAC), submitted_at, is_public (¿se publica en perfil del restaurante?).
- `AIResponse`: review_id, response_text, generated_at, was_used (booleano), edited_text (opcional, si el restaurante editó antes de enviar).

## Reglas duras

1. **`public_token`** se genera con HMAC-SHA256 de `(review_id + secret)`. Vida útil: 30 días. Verificación en `domain/services.py:TokenService`.
2. **Endpoint público `/api/v1/reviews/public/{token}`** es el ÚNICO sin auth. Validación estricta: token válido + no expirado + no usado.
3. **Generación de IA** llama vía HTTP a `/api/v1/ai/review-response` (contexto `ai/`). NUNCA importes OpenAI directo aquí.
4. **Cron de envío post-visita**: `internal_cron/send-review-requests` corre cada 10min, busca reservas `completed` hace 2-3h sin review request enviado, dispara WhatsApp con link.
5. **Rating de 1-2 estrellas** marca la review como `requires_attention` y notifica al owner (futuro: feature post-MVP).

## Endpoints

- `GET /api/v1/reviews` (lista para staff, filtros por rating/date)
- `POST /api/v1/reviews/{id}/ai-response` (genera respuesta IA)
- `POST /api/v1/reviews/{id}/respond` (publica respuesta del restaurante — vía DM al cliente)
- `GET /api/v1/reviews/public/{token}` — formulario público (devuelve metadata del restaurante)
- `POST /api/v1/reviews/public/{token}` — cliente submitea rating + comentario
