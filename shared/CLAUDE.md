# shared/ — Contrato cross-lenguaje (Python ↔ TypeScript)

> Reglas globales: [/CLAUDE.md](../CLAUDE.md).

## Propósito

Una sola fuente de verdad para tipos compartidos entre backend (FastAPI) y frontend (Tauri/React).

```
shared/
├── openapi.json          # GENERADO — schema OpenAPI unificado de todas las Vercel Functions
├── types.ts              # GENERADO — tipos TypeScript de OpenAPI (openapi-typescript)
└── database.types.ts     # GENERADO — tipos TS del schema Supabase (supabase gen types)
```

## Reglas duras

1. **NUNCA editar archivos en `shared/` a mano.** Todos son **generados**. Cambios manuales se pierden en el próximo build.

2. **Generación es step de CI**, también disponible local:
   ```bash
   make generate-types
   # ↓ equivale a:
   #   cd backend && uv run python scripts/export_openapi.py > ../shared/openapi.json
   #   pnpm dlx openapi-typescript shared/openapi.json -o shared/types.ts
   #   supabase gen types typescript --local > shared/database.types.ts
   ```

3. **Cuando cambies un DTO en backend:**
   - Edita `backend/src/contexts/<x>/interface/dtos.py`
   - Corre `make generate-types`
   - Commitea AMBOS: el cambio en backend + los archivos generados en `shared/`
   - CI valida que `shared/` esté en sync (diff fails → PR bloqueado)

4. **Tauri importa siempre de `shared/`:**
   ```ts
   import type { paths, components } from '../../shared/types';
   import type { Database } from '../../shared/database.types';
   ```

5. **Backend NO importa de `shared/`** — backend es la fuente; `shared/` es output.

## Generación de OpenAPI unificado

Como cada Vercel Function es una FastAPI independiente, su `/openapi.json` cubre solo sus rutas. `backend/scripts/export_openapi.py` instancia todos los routers, mergea en un solo schema, lo escribe en `shared/openapi.json`.

```python
# backend/scripts/export_openapi.py (esqueleto)
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

# importa routers de todos los contextos
from src.contexts.identity.interface.router import router as identity_router
# ...

app = FastAPI(title="Connek Restaurant OS", version="0.1.0")
app.include_router(identity_router, prefix="/api/v1")
# ... include all routers

schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
print(json.dumps(schema, indent=2))
```

## .gitattributes

Considera marcar `shared/types.ts` y `shared/database.types.ts` como `linguist-generated=true` en `.gitattributes` para que GitHub colapse el diff y no lo muestre como "humano".
