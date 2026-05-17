# backend/tests/ — Suite de tests

> Reglas globales: [/CLAUDE.md](../../CLAUDE.md), [/backend/CLAUDE.md](../CLAUDE.md).

## Filosofía

- **Dominio = 100% cobertura.** State machines, value objects, business rules: cero excusas.
- **Application = 90%+.** Use cases con mocks de Protocols.
- **Infrastructure = integration tests con Supabase local.** Sin mocks de DB ni de RLS.
- **E2E = solo flujos críticos.** Hagamos pocos, pero que sean LOS importantes.

## Estructura

```
tests/
├── conftest.py            # fixtures globales (db session, factories, JWT helpers)
├── unit/
│   ├── shared/            # tests de shared kernel
│   └── contexts/<x>/
│       ├── domain/        # tests del state machine y entities
│       └── application/   # tests de use cases con mocks
├── integration/
│   ├── test_tenancy.py    # ⚠️ BLOQUEANTE en CI — RLS aislamiento
│   └── contexts/<x>/
│       └── infrastructure/ # tests de repositories contra Supabase local
└── e2e/
    ├── test_reservation_flow.py      # signup → reserva → SMS → seat → review
    ├── test_waitlist_flow.py
    ├── test_billing_flow.py          # trial → upgrade → webhook
    └── test_admin_impersonate.py
```

## Reglas duras

1. **`test_tenancy.py` es BLOQUEANTE.** Si un test crea org A + org B y la consulta de A devuelve filas de B, el merge no entra. CI debe fallar duro.

2. **Sin mocks en integration tests.** Usa Supabase local (`supabase start` levanta Postgres + Auth + Realtime local).

3. **Cada test es independiente.** Usa `pytest-asyncio` + fixtures con `scope="function"`. Si dos tests se influencian, está mal.

4. **`factory_boy` es la fuente de fixtures.** Crea factories en `backend/src/factories/`. NUNCA hardcodear UUIDs o datos en el test directamente.

5. **Naming**: `test_<lo_que_prueba>_<cuando>` — `test_seat_reservation_when_already_seated_raises_error`.

6. **Un assert por test cuando sea posible**, varios cuando comparten setup costoso.

7. **Cobertura mínima en CI: 70%.** PR que la baje → bloqueado.

## Comandos

```bash
uv run pytest                                    # todo
uv run pytest tests/unit                         # rápido
uv run pytest tests/integration -m "not slow"    # integration sin pruebas pesadas
uv run pytest -k tenancy                         # filtrar
uv run pytest --cov=src --cov-report=html        # reporte HTML
uv run pytest -x                                 # parar en primera falla
uv run pytest --lf                               # solo los que fallaron antes
```

## Setup local

```bash
# levantar Supabase local
supabase start

# aplicar migraciones
supabase db reset

# correr tests
uv run pytest
```
