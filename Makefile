.DEFAULT_GOAL := help

# ─── Helpers ─────────────────────────────────────────────────────
.PHONY: help
help: ## Lista comandos disponibles
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ─── Setup ───────────────────────────────────────────────────────
.PHONY: install
install: install-backend install-desktop ## Instala todas las deps

.PHONY: install-backend
install-backend: ## Instala deps Python con uv
	cd backend && uv sync

.PHONY: install-desktop
install-desktop: ## Instala deps Node con pnpm
	cd desktop && pnpm install

# ─── Supabase local ──────────────────────────────────────────────
.PHONY: supabase-start
supabase-start: ## Levanta Supabase local (Postgres + Auth + Realtime + Studio)
	supabase start

.PHONY: supabase-stop
supabase-stop: ## Para Supabase local
	supabase stop

.PHONY: supabase-reset
supabase-reset: ## Resetea DB local y aplica migraciones + seed
	supabase db reset

.PHONY: supabase-status
supabase-status: ## Muestra URLs y keys locales
	supabase status

# ─── Dev servers ─────────────────────────────────────────────────
.PHONY: dev-backend
dev-backend: ## Backend FastAPI en modo dev (todos los contexts montados)
	cd backend && uv run uvicorn src.main_dev:app --reload --port 8000

.PHONY: dev-desktop
dev-desktop: ## Desktop Tauri en modo dev
	cd desktop && pnpm tauri dev

# ─── Migraciones ─────────────────────────────────────────────────
.PHONY: migrate
migrate: ## Aplica migraciones Alembic en local
	cd backend && uv run alembic upgrade head

.PHONY: migration
migration: ## Crea nueva migración Alembic (uso: make migration name="add reservations")
	cd backend && uv run alembic revision --autogenerate -m "$(name)"

# ─── Tests ───────────────────────────────────────────────────────
.PHONY: test
test: test-backend ## Corre toda la suite

.PHONY: test-backend
test-backend: ## Tests Python
	cd backend && uv run pytest

.PHONY: test-unit
test-unit: ## Solo unit tests (rápido)
	cd backend && uv run pytest tests/unit

.PHONY: test-integration
test-integration: ## Tests integration (requiere supabase local)
	cd backend && uv run pytest tests/integration

.PHONY: test-tenancy
test-tenancy: ## ⚠️ Test bloqueante de aislamiento RLS
	cd backend && uv run pytest tests/integration/test_tenancy.py -v

.PHONY: test-coverage
test-coverage: ## Tests + reporte cobertura HTML
	cd backend && uv run pytest --cov=src --cov-report=html
	@echo "Open backend/htmlcov/index.html"

# ─── Lint / Typecheck ────────────────────────────────────────────
.PHONY: lint
lint: lint-backend lint-desktop ## Lint todo

.PHONY: lint-backend
lint-backend:
	cd backend && uv run ruff check . && uv run ruff format --check .

.PHONY: lint-desktop
lint-desktop:
	cd desktop && pnpm lint

.PHONY: fmt
fmt: ## Auto-format
	cd backend && uv run ruff format . && uv run ruff check --fix .
	cd desktop && pnpm format

.PHONY: typecheck
typecheck: ## Typecheck todo
	cd backend && uv run mypy src
	cd desktop && pnpm typecheck

# ─── Schema sharing ──────────────────────────────────────────────
.PHONY: generate-types
generate-types: ## Genera shared/openapi.json + shared/types.ts + shared/database.types.ts
	cd backend && uv run python scripts/export_openapi.py > ../shared/openapi.json
	cd desktop && pnpm dlx openapi-typescript ../shared/openapi.json -o ../shared/types.ts
	supabase gen types typescript --local > shared/database.types.ts

# ─── Seeds ───────────────────────────────────────────────────────
.PHONY: seed-demo
seed-demo: ## Carga datos de demo en DB local
	cd backend && uv run python scripts/seed_demo.py

# ─── Vercel ──────────────────────────────────────────────────────
.PHONY: vercel-link
vercel-link: ## Vincula repo local con proyecto Vercel (interactivo)
	vercel link

.PHONY: vercel-env-pull
vercel-env-pull: ## Descarga env vars de Vercel a .env.vercel.local
	vercel env pull .env.vercel.local

.PHONY: vercel-env-add
vercel-env-add: ## Agrega var a Vercel (uso: make vercel-env-add name=KEY value=VAL env=production)
	@echo "$(value)" | vercel env add $(name) $(env)

.PHONY: vercel-dev
vercel-dev: ## Corre Vercel dev local (emula serverless functions)
	vercel dev

.PHONY: vercel-validate
vercel-validate: ## Valida vercel.json (sintaxis + functions existen)
	@python -c "import json; json.load(open('vercel.json'))" && echo "✓ vercel.json es JSON válido"
	@python -c "import json, pathlib, sys; cfg=json.load(open('vercel.json')); m=[f for f in cfg.get('functions',{}) if not pathlib.Path(f).exists()]; sys.exit(1) if m else print(f'✓ Las {len(cfg[\"functions\"])} functions existen')"

.PHONY: deploy-preview
deploy-preview: vercel-validate ## Deploy preview a Vercel
	vercel

.PHONY: deploy-prod
deploy-prod: vercel-validate ## Deploy production a Vercel (cuidado)
	vercel --prod

.PHONY: deploy-status
deploy-status: ## Ver últimos deploys del proyecto
	vercel ls --confirm

.PHONY: deploy-logs
deploy-logs: ## Logs en vivo del último deploy
	vercel logs $$(vercel ls --confirm 2>/dev/null | head -2 | tail -1 | awk '{print $$2}') --follow

# ─── Limpieza ────────────────────────────────────────────────────
.PHONY: clean
clean: ## Limpia caches y builds
	rm -rf backend/.pytest_cache backend/.mypy_cache backend/.ruff_cache backend/htmlcov backend/.coverage
	rm -rf desktop/node_modules desktop/dist desktop/src-tauri/target

.PHONY: clean-py
clean-py:
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
