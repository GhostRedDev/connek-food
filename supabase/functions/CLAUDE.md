# supabase/functions/ — Edge Functions (Deno)

> Reglas globales: [/CLAUDE.md](../../CLAUDE.md), [/supabase/CLAUDE.md](../CLAUDE.md).

## Cuándo usar Edge Functions

**Pocas veces.** Default: pon la lógica en FastAPI.

Casos legítimos:
- Webhook que debe responder en <50ms y vive cerca de Supabase (no aceptable un cold start de Vercel Function Python).
- Lógica que requiere acceso directo al `service-role` con la menor superficie de ataque posible.
- Edge Functions de Auth hooks (custom claims, send sms hooks).

## Reglas duras

1. **Justifica en el README de la function por qué NO está en FastAPI.**
2. **TypeScript con tipos estrictos** (Deno). NO `any`.
3. **Validación con Zod** en input.
4. **Sin lógica de negocio compleja** — solo orquestación rápida.
5. **Auth hooks** (custom JWT claims, send SMS, send email) cuando sea necesario sobreescribir defaults de Supabase.

## Estructura

```
functions/
└── <nombre>/
    ├── index.ts
    ├── README.md         # por qué existe esta function
    └── deno.json
```

## Comandos

```bash
supabase functions new <name>
supabase functions serve <name>              # local
supabase functions deploy <name> --no-verify-jwt   # si es webhook público
```

## MVP: probablemente vacío

En el MVP de 30 días, todo va a FastAPI. Esta carpeta puede quedar sin functions. Si la necesitas, justifica.
