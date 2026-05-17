# backend/src/contexts/ — Bounded Contexts

> Reglas en [/CLAUDE.md](../../../CLAUDE.md), [/backend/CLAUDE.md](../../CLAUDE.md), y [/backend/src/CLAUDE.md](../CLAUDE.md).

## Filosofía

Cada subcarpeta = **un bounded context** = **un microservicio** = **una Vercel Function**.

Esto es la encarnación práctica de "microservicios pragmáticos": deploys independientes, escalado por dominio, fronteras claras, **pero comparten la DB Supabase**. Cuando un contexto necesite su propia DB en el futuro, la arquitectura limpia lo permite cambiando solo `infrastructure/`.

## Lista de contextos

| Contexto | Responsabilidad | Función Vercel |
|---|---|---|
| `identity/` | Users, Organizations, Memberships, Roles | `api/identity.py` |
| `restaurants/` | Restaurant entity + Settings + Branding | `api/restaurants.py` |
| `reservations/` | Reserva + estados + calendar/timeline | `api/reservations.py` |
| `floor/` | Mesas + FloorPlan + transiciones | `api/floor.py` |
| `waitlist/` | Lista de espera + wait time + notify | `api/waitlist.py` |
| `clients/` | CRM clientes + visitas + historial | `api/clients.py` |
| `communications/` | Templates + envío SMS/email + logs | `api/communications.py` |
| `reviews/` | Reviews + token público + responses | `api/reviews.py` |
| `ai/` | OpenAI wrapper + chat + suggestions | `api/ai.py` |
| `staff/` | StaffMembers + Shifts | `api/staff.py` |
| `billing/` | Stripe subscriptions + plan limits | `api/billing.py` |
| `admin/` | Super-admin views (bypass tenant) | `api/admin.py` |

## Reglas duras

### 1. AISLAMIENTO ESTRICTO entre contextos

**PROHIBIDO** importar de otro contexto:
```python
# ❌ NO
from src.contexts.reservations.domain.entities import Reservation
# dentro de src/contexts/waitlist/...

# ✅ SÍ — comunicación vía DB o HTTP
# (lee la reserva desde tabla, o llama al endpoint /reservations/{id})
```

Si dos contextos necesitan compartir una entidad, una de estas:
- **El dato vive en uno y el otro consulta vía DB** (preferido para reads).
- **El dato vive en uno y el otro llama vía HTTP** (preferido para escrituras).
- **Extraer a `shared/domain/`** (último recurso — implica que es un concepto cross-cutting de verdad).

### 2. Plantilla de Clean Architecture (idéntica en todos los contextos)

```
<context>/
├── __init__.py
├── CLAUDE.md                  # describe el contexto específico
├── domain/
│   ├── __init__.py
│   ├── entities.py            # Reservation, Client, etc.
│   ├── value_objects.py       # PartySize, TimeSlot, etc.
│   ├── repositories.py        # Protocols (interfaces)
│   ├── services.py            # domain services (lógica que no encaja en entity)
│   └── errors.py              # ReservationError, InvalidStateTransition, etc.
├── application/
│   ├── __init__.py
│   ├── commands.py            # dataclasses de inputs de use cases
│   ├── queries.py             # dataclasses de inputs de queries
│   └── use_cases.py           # CreateReservationUseCase, SeatReservationUseCase, etc.
├── infrastructure/
│   ├── __init__.py
│   ├── models.py              # SQLAlchemy ORM models (mapeo de Reservation entity)
│   ├── repositories.py        # implementaciones de Protocols del dominio
│   └── adapters.py            # adapters externos (Twilio, OpenAI, etc.) si aplican
└── interface/
    ├── __init__.py
    ├── router.py              # FastAPI APIRouter
    ├── dtos.py                # Pydantic in/out DTOs
    └── dependencies.py        # factories de use cases para Depends()
```

### 3. Mapeo Entity ↔ ORM model

- `domain/entities.py` → puro Python (`@dataclass` o `pydantic.BaseModel` sin `from_orm`).
- `infrastructure/models.py` → `Base = declarative_base()` de SQLAlchemy.
- `infrastructure/repositories.py` → traduce entre ambos (`def _to_entity(model) -> Entity`, `def _to_model(entity) -> Model`).

NUNCA exponer un SQLAlchemy model fuera de `infrastructure/`.

### 4. Naming consistente

- Use case names: verbo + sustantivo + `UseCase`. `CreateReservationUseCase`, `NotifyWaitlistEntryUseCase`.
- Command names: verbo + sustantivo + `Command`. `CreateReservationCommand`.
- Query names: `Get<X>Query`, `List<X>Query`.
- DTO names: `<Resource>InputDTO`, `<Resource>OutputDTO`.
- Router prefix: `/<context>` (en singular si es agregado, plural si es colección).

### 5. Crear un nuevo contexto = copiar `identity/`

`identity/` es el contexto de referencia. Cuando crees uno nuevo:
1. `cp -r identity/ <new_context>/`
2. Renombra todas las entidades.
3. Reemplaza la lógica.
4. Actualiza este CLAUDE.md (tabla de contextos).
5. Crea `api/<new_context>.py` siguiendo el template de `backend/api/CLAUDE.md`.
6. Agrega entry en `vercel.ts`.

## Anti-patrones

- ❌ Compartir `domain/entities.py` entre contextos (extrae a `shared/domain/` o duplica).
- ❌ Importar `infrastructure/` desde `application/` (rompe DI).
- ❌ Lógica de negocio en `interface/router.py` (debe ir a use case).
- ❌ Llamar Supabase/Stripe/OpenAI directo desde `application/` (envuelve en `infrastructure/`).
