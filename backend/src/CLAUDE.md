# backend/src/ — Código de aplicación

> Reglas en [/CLAUDE.md](../../CLAUDE.md) y [/backend/CLAUDE.md](../CLAUDE.md).

## Estructura

```
src/
├── shared/      → shared kernel (todo lo que cruza contextos)
├── contexts/    → bounded contexts (1 carpeta por dominio = 1 microservicio)
└── factories/   → factory_boy fixtures para tests
```

## Reglas duras

1. **Todo código nuevo va dentro de `shared/` o `contexts/<x>/`.** No flotando en `src/`.
2. **No agregues archivos sueltos aquí.** Si necesitas un `main.py` para dev local, ponlo y agrégalo a este readme.
3. **Imports absolutos:** `from src.shared.errors import ...`, nunca relativos largos.
4. **Cada contexto es independiente:** lee [contexts/CLAUDE.md](contexts/CLAUDE.md).

## Archivos especiales permitidos

- `main_dev.py`: opcional, monta todos los contexts en un solo app FastAPI para desarrollo local (`uv run uvicorn src.main_dev:app --reload`). NO se usa en producción.
- `__init__.py` vacíos donde Python los requiera.
