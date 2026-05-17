# .github/ — CI/CD, workflows, configuración GitHub

> Reglas globales: [/CLAUDE.md](../CLAUDE.md).

## Filosofía

CI debe ser **rápido, paralelo y predecible**. Solo corre los jobs cuyos paths cambiaron (vía `dorny/paths-filter`). PRs no se mergean sin CI verde.

## Workflows

| Archivo | Trigger | Qué hace | Bloqueante para merge |
|---|---|---|---|
| `ci.yml` | PR + push main | Lint + typecheck + tests backend & desktop, valida vercel.json | ✅ |
| `shared-sync.yml` | PR que toca DTOs o shared/ | Verifica que `shared/types.ts` esté regenerado | ✅ |
| `test-tenancy.yml` | PR que toca backend o migraciones | Test de aislamiento RLS multi-tenant | ✅ |

## Reglas duras

1. **Vercel hace los preview deploys** — NO duplicar deploy logic en GitHub Actions. Vercel detecta el push a la rama del PR y crea preview URL automáticamente (requiere vincular el proyecto con `vercel link`).

2. **Concurrency**: cada workflow cancela runs viejos del mismo PR (`cancel-in-progress: true`). No malgastar minutos de GitHub Actions.

3. **Path filters obligatorios**: si tu PR no toca backend, el job de backend no debe correr. `dorny/paths-filter@v3`.

4. **Secrets en GitHub Settings**, no hardcoded:
   - `VERCEL_TOKEN` (opcional — solo si haces deploy manual)
   - `SUPABASE_ACCESS_TOKEN` (si en algún momento necesitas push de migraciones desde CI)
   - Nada de OPENAI / TWILIO / STRIPE keys en CI — los tests usan mocks o valores fake.

5. **No skip-ci en main**: `[skip ci]` está prohibido en commits a main. Solo permitido en branches de docs/typo.

6. **Branch protection en main:**
   - PR obligatorio (no push directo)
   - CI verde requerido
   - 1 approve mínimo (cuando el equipo crezca)
   - Dismiss stale reviews al hacer force-push

## Convención de PRs

- **Título:** imperativo presente, <70 chars. Ej: `add reservation seat use case`.
- **Body:** qué + por qué + cómo testear. Referencia al plan o issue.
- **Branch naming:** `feature/<descripcion>`, `fix/<bug>`, `chore/<tooling>`, `refactor/<scope>`.
- **Tamaño:** <500 líneas neto cuando sea posible. PRs gigantes son humanamente irrevisables.

## Setup inicial (humano debe hacer una vez)

1. **Crear repo en GitHub** (`gh repo create connek/connek-food --private --source=. --remote=origin`).
2. **Push inicial** (`git push -u origin main`).
3. **Conectar Vercel** al repo desde dashboard Vercel o `vercel link` desde CLI.
4. **Configurar secrets** en `Settings → Secrets and variables → Actions` (solo los que CI necesita).
5. **Activar branch protection** en `main` (`Settings → Branches → Add rule`).
6. **Provisionar Supabase project** desde dashboard Supabase o `supabase projects create`.

## Cuándo agregar un workflow nuevo

Pregúntate:
- ¿Esto debería bloquear un merge? Si no, NO es un workflow CI — quizás es un script en `backend/scripts/`.
- ¿Vercel ya lo hace? Si Vercel ya despliega previews y maneja env vars por entorno, no dupliques.
- ¿Puede vivir como un job dentro de `ci.yml` en vez de archivo separado? Probablemente sí, salvo que tenga triggers muy distintos.
