# desktop/src/lib/ — Clientes y utilidades globales

> Reglas globales: [/CLAUDE.md](../../../CLAUDE.md), [/desktop/CLAUDE.md](../../CLAUDE.md).

## Qué vive aquí

Singletons, configuración global, helpers que no son UI.

```
lib/
├── supabase.ts          # cliente supabase-js — UNA sola instancia
├── api.ts               # cliente openapi-fetch hacia FastAPI
├── auth-store.ts        # Zustand store: session + activeOrgId
├── query-client.ts      # TanStack QueryClient config
├── date.ts              # helpers de fecha (timezone, formato)
├── i18n.ts              # opcional, MVP solo ES
└── constants.ts         # URLs base, feature flags
```

## Reglas duras

1. **`supabase.ts` exporta UN solo cliente.** Si necesitas service-role en frontend, NO LO HAGAS (eso es backend).
2. **`api.ts` se construye CON el JWT del usuario** (de Supabase Auth). Si no hay sesión, los calls fallan (intencional).
3. **`auth-store.ts`** persiste en `localStorage` con Zustand `persist`. Limpia al logout.
4. **NO componentes React aquí.** Si necesitas un Provider, ponlo en `App.tsx` o crea `components/<Provider>.tsx`.
5. **NO lógica de negocio.** Solo plomería.

## Template: `lib/supabase.ts`

```ts
import { createClient } from '@supabase/supabase-js';
import type { Database } from '../../../shared/database.types';

export const supabase = createClient<Database>(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY,
  {
    auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true },
    realtime: { params: { eventsPerSecond: 10 } },
  },
);
```

## Template: `lib/api.ts`

```ts
import createClient from 'openapi-fetch';
import type { paths } from '../../../shared/types';
import { supabase } from './supabase';
import { useAuthStore } from './auth-store';

export const api = createClient<paths>({
  baseUrl: import.meta.env.VITE_API_URL,
});

api.use({
  async onRequest({ request }) {
    const { data: { session } } = await supabase.auth.getSession();
    if (session) request.headers.set('Authorization', `Bearer ${session.access_token}`);
    const orgId = useAuthStore.getState().activeOrgId;
    if (orgId) request.headers.set('X-Organization-Id', orgId);
    return request;
  },
});
```
