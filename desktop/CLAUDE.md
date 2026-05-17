# desktop/ — Tauri 2 + React 19 + TypeScript

> Reglas globales: [/CLAUDE.md](../CLAUDE.md). Este archivo manda dentro de `desktop/`.

## Propósito

App desktop cross-platform (macOS, Windows, Linux) que usa el restaurante en su iPad/laptop. Construida con Tauri 2 (Rust shell) + React 19 + TypeScript + Tailwind + shadcn/ui.

## Filosofía visual (del plan original)

- **Apple-like**: limpio, ultra moderno, glass subtle, light mode primario.
- **Tarjetas grandes, mucho blanco**, sombras suaves, tipografía premium.
- **Azul eléctrico CONNEK** como acento.
- Referencias: Stripe, Notion, Linear, SevenRooms, OpenTable.
- **Velocidad sobre todo.** Cada milisegundo de latencia es un cliente perdido.

## Tooling

- **Runtime:** Node 22 LTS, Bun como runner opcional.
- **Package manager:** `pnpm` (no npm, no yarn).
- **Bundler:** Vite (default de Tauri).
- **Tauri:** v2.
- **React:** v19.
- **CSS:** Tailwind v4 + shadcn/ui (configurado vía `pnpm dlx shadcn@latest init`).
- **State:** Zustand para client state + TanStack Query para server state.
- **Forms:** react-hook-form + zod.
- **HTTP:** `openapi-fetch` consumiendo `shared/types.ts`.

## Estructura

```
desktop/
├── package.json
├── tsconfig.json
├── tauri.conf.json
├── vite.config.ts
├── tailwind.config.ts
├── src-tauri/                 # Rust (Tauri)
│   ├── tauri.conf.json
│   ├── Cargo.toml
│   └── src/
├── src/                       # React
│   ├── App.tsx
│   ├── main.tsx
│   ├── lib/                   # clientes y utilidades cross-cutting
│   │   ├── supabase.ts        # cliente supabase-js singleton
│   │   ├── api.ts             # cliente FastAPI tipado (openapi-fetch)
│   │   ├── auth-store.ts      # Zustand: sesión actual + org activa
│   │   └── query-client.ts    # TanStack Query config
│   ├── components/            # UI compartida (shadcn/ui + custom)
│   │   └── ui/                # shadcn/ui generated
│   ├── features/              # mirror de bounded contexts del backend
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── reservations/
│   │   ├── floor/
│   │   ├── waitlist/
│   │   ├── clients/
│   │   ├── reviews/
│   │   ├── settings/
│   │   ├── staff/
│   │   └── admin/             # solo visible si role === super_admin
│   └── routes/                # routing (React Router o TanStack Router)
└── public/
```

## Reglas duras

### 1. Tauri ↔ Supabase ↔ FastAPI — quién habla con quién

- **Auth** (login/signup/JWT/password reset): `lib/supabase.ts` directo. NUNCA pasar por FastAPI.
- **Realtime** (mesas, waitlist, reservas en vivo): `supabase.channel(...).on('postgres_changes', ...)`. NUNCA polling o WebSocket custom.
- **Storage** (subir logo, fotos): `supabase.storage.from(bucket).upload(...)`. NUNCA proxy por FastAPI.
- **Business logic / IA / WhatsApp / Stripe**: `lib/api.ts` → FastAPI.

### 2. Tipos del backend = `shared/types.ts`

NUNCA hardcodees DTOs. Importa de `../../shared/types.ts`:
```ts
import type { components } from '../../shared/types';
type Reservation = components['schemas']['ReservationOutputDTO'];
```

Si el tipo no existe ahí, ABRE issue en backend para que se exponga en OpenAPI. No inventes tipos.

### 3. Features espejean contexts del backend

`desktop/src/features/<x>/` ↔ `backend/src/contexts/<x>/`. Cada feature tiene:
```
features/<x>/
├── pages/             # rutas top-level (e.g. ReservationsListPage)
├── components/        # UI específica del feature
├── hooks/             # TanStack Query hooks (useReservations, useCreateReservation)
└── types.ts           # tipos derivados o re-exports de shared/types
```

NUNCA imports cross-feature (`from features/X` desde `features/Y`). Si necesitan algo común, va a `components/` o `lib/`.

### 4. Estilo

- **Tailwind con design tokens**. Define colores Connek en `tailwind.config.ts`.
- **shadcn/ui es la base**. Personaliza componentes en `components/ui/`, no los uses raw.
- **No CSS modules, no styled-components.** Tailwind únicamente.
- **Dark mode**: NO en MVP. Solo light. Post-MVP.

### 5. Performance

- **TanStack Query**: configuración default `staleTime: 30s`, `gcTime: 5min`. Override por hook si necesario.
- **Lazy loading routes** con `React.lazy`.
- **Imágenes**: usa `<img loading="lazy">` o `Image` de Tauri. Logos via Supabase Storage CDN.
- **Bundle size objetivo**: <1MB inicial (excluyendo runtime Tauri).

### 6. Accesibilidad

- shadcn/ui ya viene accesible. NO rompas con `div onClick`.
- Labels en forms (`<Label htmlFor>`).
- Colores con contraste WCAG AA mínimo.

## Comandos

```bash
cd desktop
pnpm install
pnpm tauri dev                          # desarrollo
pnpm tauri build                        # build production
pnpm typecheck                          # tsc --noEmit
pnpm lint                               # eslint + prettier
pnpm test                               # vitest
pnpm shadcn add button                  # agregar componente shadcn
```

## Anti-patrones

- ❌ Lógica de negocio en componentes (extrae a hooks o lib).
- ❌ `fetch()` raw — usa `lib/api.ts` (openapi-fetch).
- ❌ Supabase client en cada componente — usa el singleton de `lib/supabase.ts`.
- ❌ `useState` para datos del servidor — usa TanStack Query.
- ❌ Polling — usa Supabase Realtime.
- ❌ Inventar tipos de DTOs — importa de `shared/types.ts`.
