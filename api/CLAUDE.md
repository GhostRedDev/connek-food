# api/ — Vercel Functions entrypoints (root)

> Reglas globales: [/CLAUDE.md](../CLAUDE.md), [/backend/CLAUDE.md](../backend/CLAUDE.md).

## Por qué está en el root y no en `backend/`

Vercel exige que las Serverless Functions vivan en `/api/` al nivel raíz del repo. No es opcional: el builder Python solo escanea `/api/`.

Convivimos así:
- **`/api/`** → shells de Vercel (código mínimo, sin lógica de negocio)
- **`/backend/src/`** → todo el código real (Clean Architecture)

## Estado actual: modular monolith (no microservicios)

Plan original: una function por bounded context (12 contexts → 12 Vercel Functions). **Realidad MVP**: Hobby free plan limita # functions + costo de instalar `requirements.txt` completo por cada function. Por eso ahora hay **solo 2 functions**:

| Archivo | Propósito | Bundle |
|---|---|---|
| `health.py` | Smoke-test sin deps (solo Python stdlib + FastAPI) | <10MB |
| `index.py` | Monta TODOS los routers de `backend/src/contexts/*` en un solo FastAPI | crece a medida que se implementan contexts |

**Clean Architecture intacta:** cada bounded context sigue viviendo aislado en `backend/src/contexts/<x>/`. Solo el deploy es monolítico. Cuando una vertical justifique escala/aislamiento independiente (y estés en Pro plan), se extrae a su propia function copiando el template — el cambio es mecánico porque las fronteras de dominio están bien.

## Reglas duras

1. **NO agregues más archivos `.py` aquí** sin justificar (hablar con el humano). Si necesitas una nueva ruta, mútala en un router de `backend/src/contexts/<x>/interface/router.py` y monta en `index.py`.

2. **`health.py` debe permanecer mínimo.** Sin imports de SQLAlchemy/Supabase/OpenAI/etc. Es el endpoint que pinga el frontend cada 10s para mostrar status — debe responder en <50ms y nunca caerse por dependencias.

3. **`index.py` es el monolito modular.** Importa routers de los contexts a medida que existen. Cada `include_router(prefix='/api/v1/<context>')` los expone bajo el path correcto.

4. **`sys.path.insert(0, '../backend')`** ya está en `index.py` para que `from src.contexts.X.interface.router import router` funcione.

5. **Vercel routing:** `vercel.json` mapea:
   - `/api/v1/health*` → `api/health.py`
   - `/api/v1/*` → `api/index.py` (catch-all)

## Cuando implementes un nuevo bounded context

1. Implementa `backend/src/contexts/<x>/` (domain → application → infrastructure → interface).
2. En `interface/router.py` expone un `APIRouter()` con todas las rutas del contexto.
3. En `api/index.py`, descomenta (o agrega) la importación y `include_router(...)`.
4. Si el contexto necesita dependencias Python nuevas, agrégalas a `requirements.txt` (root) y al `pyproject.toml` (backend).
5. Tests + deploy.

## Cuando llegue el día de splittear a microservicios real

(post-MVP, con Pro plan, cuando algún contexto necesite escala/cold-start propio)

1. Copia `api/index.py` → `api/<context>.py`.
2. Deja en `<context>.py` SOLO el router de ese contexto.
3. Saca de `index.py` el `include_router` correspondiente.
4. Agrega entry en `vercel.json` (`functions` + `rewrites`).
5. Listo: deploy independiente, cold start propio, escala propia.

No reescribes nada del dominio — eso ya estaba aislado desde el día 1.
