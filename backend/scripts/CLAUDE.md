# backend/scripts/ — Scripts operacionales

> Reglas globales: [/CLAUDE.md](../../CLAUDE.md).

## Propósito

One-off scripts y utilidades que no son endpoints HTTP ni tests. Seeds, migraciones de datos, exports, debugging.

## Scripts esperados

- `seed_demo.py` — crea 1 org + 1 restaurante + 30 reservas + 50 clientes + 15 mesas + 20 reviews. Usado en demos y onboarding de nuevos devs.
- `export_openapi.py` — extrae el schema OpenAPI de cada context y mergea en `shared/openapi.json`. Se ejecuta en CI antes de generar `shared/types.ts`.
- `backfill_<x>.py` — ad-hoc cuando una migración de datos sea necesaria. NOMBRA CON FECHA: `backfill_clients_phone_normalize_2026_05_20.py`.

## Reglas duras

1. **Todo script imprime qué va a hacer ANTES de hacerlo** (modo dry-run por defecto cuando aplique).
2. **Service-role permitido aquí** (bypass RLS) cuando sea operacional. Justifica en comentario al principio del archivo.
3. **Scripts que tocan producción** requieren flag `--prod` explícito + confirmación interactiva. NUNCA por accidente.
4. **Logs estructurados** (usa `shared/telemetry.py`).
5. **Idempotentes cuando sea posible** — corre 2 veces, mismo resultado.

## Ejecución

```bash
uv run python scripts/seed_demo.py
uv run python scripts/export_openapi.py > ../shared/openapi.json
uv run python scripts/backfill_x.py --dry-run
uv run python scripts/backfill_x.py --prod
```
