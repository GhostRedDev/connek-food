# ai/ — OpenAI wrapper + chat + suggestions

> Reglas globales: [/CLAUDE.md](../../../../CLAUDE.md).

## Responsabilidad

Único contexto que habla con OpenAI. Centraliza prompts, manejo de tokens, streaming, fallbacks. Otros contextos NO importan `openai` — llaman a estos endpoints.

## Capacidades

- **Review response**: dado un review, genera respuesta con tono del restaurante (de `restaurant.settings.branding`).
- **Suggest slots**: dado party_size + fecha preferida, devuelve top-3 horarios disponibles considerando ocupación.
- **Assistant chat**: SSE streaming para asistente FAQ (¿qué horario?, ¿hay parking?, etc.).

## Reglas duras

1. **Modelo default = `gpt-4o-mini`.** Configurable vía `settings.openai_model`. NUNCA hardcodear modelo en prompts.
2. **Prompts viven en `infrastructure/prompts.py`** como constantes (versión + tipo). Cuando edites, sube versión.
3. **Streaming SSE** para `/ai/chat`: usa `fastapi.responses.StreamingResponse` + async generator. Cliente Tauri consume con `EventSource`.
4. **Rate limiting / budget**: cada request loggea tokens usados en tabla `ai_usage_logs`. Si org excede plan (futuro), `BudgetExceededError`.
5. **Sin cache** en MVP. Cada llamada es fresh. Post-MVP podemos cachear respuestas estándar.
6. **Manejo de errores OpenAI**: 429/500 → reintentar con backoff 3 veces, después fallar con `AIServiceUnavailable`. NUNCA reintentar streaming a la mitad.

## Endpoints

- `POST /api/v1/ai/review-response` (body: `review_id` → genera y devuelve sin guardar; otro endpoint en `reviews/` la persiste)
- `POST /api/v1/ai/suggest-slots` (body: `party_size`, `preferred_date`, `restaurant_id`)
- `POST /api/v1/ai/chat` (body: `messages: []`, SSE response)
