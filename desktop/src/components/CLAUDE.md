# desktop/src/components/ — UI compartida

> Reglas globales: [/CLAUDE.md](../../../CLAUDE.md), [/desktop/CLAUDE.md](../../CLAUDE.md).

## Qué vive aquí

Componentes reutilizados por **2 o más features**. Si solo lo usa 1 feature, va a `features/<x>/components/`.

```
components/
├── ui/                  # shadcn/ui generated (NO editar manualmente, usa `pnpm shadcn add`)
├── layout/
│   ├── Sidebar.tsx
│   ├── Topbar.tsx
│   └── AppShell.tsx
├── data/
│   ├── DataTable.tsx    # tabla genérica con sort/filter (TanStack Table)
│   ├── EmptyState.tsx
│   └── ErrorState.tsx
├── forms/
│   ├── PhoneInput.tsx   # E.164 con bandera
│   ├── DateTimePicker.tsx
│   └── PartySizeSelect.tsx
└── feedback/
    ├── Toast.tsx        # wrapper de sonner
    └── ConfirmDialog.tsx
```

## Reglas duras

1. **`ui/` es de shadcn**. No tocar a mano — re-genera con `pnpm shadcn add <component>`.
2. **Tema Connek** vive en `components/ui/theme.ts` y `tailwind.config.ts`. Cambios de color, radii, tipografía: solo ahí.
3. **Si dudas si va aquí o en `features/<x>/components/`**, pregúntate: ¿lo usaría una segunda feature? Si no, va en features.
4. **NO lógica de negocio en componentes shared.** Solo presentación + interacción genérica.
5. **Accesible por default** (focus rings, keyboard nav, aria labels).

## Convención de props

- Booleanos prefijados con `is`/`has`/`can`: `isLoading`, `hasError`, `canEdit`.
- Callbacks prefijados con `on`: `onSave`, `onCancel`.
- Cuando uses children: prefiere componentes compuestos (`<Card><Card.Header /></Card>`) sobre props gigantes.
