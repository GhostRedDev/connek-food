# billing/ — Stripe Billing + plan limits

> Reglas globales: [/CLAUDE.md](../../../../CLAUDE.md).

## Responsabilidad

Subscripciones mensuales de los restaurantes vía Stripe. Trial → upgrade → billing portal. Cumplir límites de plan (max restaurantes, max mesas, max SMS/mes) y exponerlos al frontend.

## Entidades

- `Subscription`: organization_id (1:1), stripe_customer_id, stripe_subscription_id, plan (`free`/`pro`/`enterprise`), status (`trialing`/`active`/`past_due`/`canceled`), trial_ends_at, current_period_end.
- `Invoice`: subscription_id, stripe_invoice_id, amount, currency, status, paid_at, hosted_invoice_url.
- `PlanLimits`: enum + dataclass con límites (puede empezar hardcodeado en `domain/plan_limits.py`).

## Reglas duras

1. **Trial de 14 días automático** al crear Organization. Estado inicial = `trialing`.
2. **Webhooks de Stripe son LA verdad** del estado de subscription. Endpoint `/billing/stripe/webhook` con verificación de firma. NUNCA modificar `status` desde otro lado.
3. **Plan limits enforcement**: cada use case que crea recurso limitado verifica límite del plan ANTES. Use case helper `CheckPlanLimitUseCase` en `application/`.
4. **Bypass del trial expirado**: cuando `status='trialing'` y `trial_ends_at` pasó, la app entra en modo "upgrade required" (Tauri muestra wall).
5. **Cron `internal_cron/check-trials`** corre diario, notifica a orgs cuyo trial expira en 3 días.

## Endpoints

- `POST /api/v1/billing/checkout-session` (devuelve URL Stripe Checkout)
- `POST /api/v1/billing/portal-session` (devuelve URL portal cliente)
- `POST /api/v1/billing/stripe/webhook`
- `GET /api/v1/billing/subscription` (estado actual + plan limits)
- `GET /api/v1/billing/invoices` (lista)
