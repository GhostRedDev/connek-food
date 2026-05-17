# desktop/src/features/ — Features (espejo de bounded contexts)

> Reglas globales: [/CLAUDE.md](../../../../CLAUDE.md), [/desktop/CLAUDE.md](../../../CLAUDE.md), [/desktop/src/CLAUDE.md](../../CLAUDE.md).

## Filosofía

Cada feature aquí espejea un bounded context del backend. **Mismo nombre, mismas fronteras.** Si en backend hay `contexts/reservations/`, aquí debe haber `features/reservations/`.

## Estructura interna de cada feature

```
features/<x>/
├── pages/                # rutas top-level
│   ├── <X>ListPage.tsx
│   ├── <X>DetailPage.tsx
│   └── <X>CreatePage.tsx
├── components/           # UI específica del feature (no reusada fuera)
│   ├── <X>Card.tsx
│   ├── <X>Form.tsx
│   └── ...
├── hooks/                # TanStack Query hooks
│   ├── use<X>List.ts     # GET /api/v1/<x>
│   ├── use<X>Detail.ts   # GET /api/v1/<x>/{id}
│   ├── useCreate<X>.ts   # POST /api/v1/<x>
│   ├── useUpdate<X>.ts   # PATCH
│   ├── useDelete<X>.ts   # DELETE
│   └── use<X>Realtime.ts # Supabase Realtime subscription (cuando aplique)
├── types.ts              # re-exports de shared/types o tipos derivados
└── index.ts              # exports públicos del feature (lo que el router importa)
```

## Lista de features (mirror del backend)

| Feature | Contexto backend | Páginas principales |
|---|---|---|
| `auth/` | `identity/` | LoginPage, SignupPage, SelectOrgPage, AcceptInvitationPage |
| `dashboard/` | (transversal) | DashboardHome (cards de Hoy, Mesas, Waitlist, Reviews) |
| `reservations/` | `reservations/` | List, Calendar, Timeline, Detail, Create |
| `floor/` | `floor/` | FloorPlanPage (drag visual), TableSettingsPage |
| `waitlist/` | `waitlist/` | WaitlistPage (cola en vivo + notify button) |
| `clients/` | `clients/` | List, Detail (con history), Create |
| `reviews/` | `reviews/` | List, Detail (con AI response generator) |
| `settings/` | `restaurants/` + `communications/` | Restaurant settings, branding, templates editor |
| `staff/` | `staff/` | StaffList, ShiftsCalendar |
| `admin/` | `admin/` | (solo super_admin) OrgsList, Metrics, AuditLog |

## Reglas duras

1. **NO imports cross-feature.** Si `reservations/` necesita `Client`, lo trae de `shared/types.ts` o llama al endpoint `/clients`.
2. **Lógica de fetching SIEMPRE via TanStack Query hooks.** NO `useEffect + fetch`.
3. **Realtime via hooks dedicados.** `useFloorTablesRealtime()` se suscribe al canal Supabase, invalida queries de TanStack cuando llega un evento.
4. **Forms con react-hook-form + zod.** Schemas zod derivados de `shared/types.ts` cuando sea posible.
5. **Optimistic updates** en mutaciones críticas (seat reservation, notify waitlist) — la UX debe sentirse instantánea.

## Template: hook con realtime

```ts
// features/floor/hooks/useFloorTablesRealtime.ts
import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { supabase } from '../../../lib/supabase';

export function useFloorTablesRealtime(restaurantId: string) {
  const qc = useQueryClient();
  useEffect(() => {
    const channel = supabase
      .channel(`floor_tables:${restaurantId}`)
      .on('postgres_changes',
        { event: '*', schema: 'public', table: 'floor_tables', filter: `restaurant_id=eq.${restaurantId}` },
        () => qc.invalidateQueries({ queryKey: ['floor', 'tables', restaurantId] }))
      .subscribe();
    return () => { void supabase.removeChannel(channel); };
  }, [restaurantId, qc]);
}
```
