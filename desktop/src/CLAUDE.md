# desktop/src/ — Código React

> Reglas globales: [/CLAUDE.md](../../CLAUDE.md), [/desktop/CLAUDE.md](../CLAUDE.md).

## Estructura

```
src/
├── App.tsx              # router root
├── main.tsx             # entry
├── lib/                 # clientes y utilidades cross-cutting
├── components/          # UI compartida (shadcn/ui + custom)
├── features/            # mirror de bounded contexts
└── routes/              # opcional: definiciones de rutas si usas TanStack Router
```

## Reglas duras

1. **`lib/`** contiene SOLO singletons y utilidades genéricas (supabase client, api client, query client, helpers de fechas).
2. **`components/`** contiene UI reutilizable entre features. Si un componente solo lo usa un feature, ponlo en `features/<x>/components/`.
3. **`features/`** es donde vive el grueso del código. Cada feature es self-contained.
4. **NO imports cross-feature.** Si necesitas algo, sube a `components/` o `lib/`.
5. **Cada page tiene su archivo, no metas N pages en uno.**

## Convenciones

- Componentes: `PascalCase.tsx`.
- Hooks: `useFoo.ts`.
- Utilidades: `kebab-case.ts`.
- Tipos puros: `types.ts`.
- Constantes: `constants.ts`.
