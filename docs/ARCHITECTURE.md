# PropertyOps Architecture

PropertyOps is a production-style modular monolith for property operations.

## Runtime Topology

```text
Browser
  |
  | HTTPS
  v
React / Vite on Vercel
  |
  | REST + JWT
  v
FastAPI on Render
  |
  +--> Neon PostgreSQL
  +--> Stripe Checkout / Subscriptions
  +--> Gemini API
```

## Trust Boundaries

The frontend is not a security boundary. The backend validates:

- authenticated identity
- `ADMIN`, `OWNER`, and `TENANT` roles
- property ownership
- building/property consistency
- unit/building consistency
- lease/tenant scope
- maintenance scope
- expense scope
- rent-obligation/payment scope
- subscription ownership
- admin-only plan/subscription access
- AI property/unit scope

## Core Domain

```text
User
 |
 +-- ADMIN
 |
 +-- OWNER
 |    |
 |    +-- OwnerSubscription
 |    |      |
 |    |      +-- SubscriptionPlan
 |    |      +-- SubscriptionPayment
 |    |
 |    +-- Property
 |          |
 |          +-- Building
 |                |
 |                +-- Unit
 |                      |
 |                      +-- Lease
 |                            |
 |                            +-- TENANT
 |                            +-- RentObligation
 |                                  |
 |                                  +-- Payment
 |
 +-- TENANT
```

Operational entities also include `Maintenance`, `Expense`, `StripeEvent`, `AIAnalysisJob`, `AIInsight`, and `AIInsightEvidence`.

## Authentication and Roles

Authentication uses JWTs and hashed passwords.

Public registration creates owners only. Tenants are provisioned by owners. Admin accounts are provisioned separately.

Inactive users are rejected by the shared authentication dependency.

## Lease and Rent Scheduling

Tenancy is modeled through `Lease`, preserving history and making occupancy explicit.

The system enforces one active lease per unit.

Lease creation generates calendar-month rent obligations using the lease start day as the anchor. Short months clamp to their final day. Ending or shortening a lease cancels only applicable future pending obligations.

## Maintenance Workflow

```text
OPEN -> ASSIGNED -> IN_PROGRESS -> RESOLVED
```

Tenants create `OPEN` requests for their unit. Owners control later transitions.

## Expenses and Financials

Expenses have an explicit owner.

```text
Property expense:
owner_id = owner
property_id = property
unit_id = optional

General expense:
owner_id = owner
property_id = NULL
unit_id = NULL
maintenance_id = NULL
```

Owner financial reporting aggregates:

- paid rent by `paid_at`
- property and general expenses by `expense_date`
- net cash flow
- pending rent obligations
- daily or monthly chart buckets

## Rent Payment Architecture

Browser redirects never establish payment truth.

```text
Tenant starts Checkout
  |
  v
Payment -> PROCESSING
  |
  v
Stripe checkout.session.completed
  |
  v
Signature verification
Event idempotency
Session/amount/currency validation
  |
  v
Payment -> PAID
RentObligation -> PAID
```

Owners can also record cash rent payments. Paid rent can generate a PDF receipt.

## Subscription Billing Architecture

Rent and owner subscriptions reuse one Stripe account and one signed webhook endpoint.

```text
Rent:
Checkout mode=payment
metadata.flow=RENT

Owner subscription:
Checkout mode=subscription
metadata.flow=SUBSCRIPTION
```

Subscription states:

```text
FREE
INCOMPLETE
ACTIVE
PAST_DUE
CANCELED
```

Paid property limits are effective only when the paid subscription is `ACTIVE`.

```text
FREE                 -> Free limit
INCOMPLETE paid plan -> Free limit
ACTIVE paid plan     -> Paid-plan limit
PAST_DUE paid plan   -> Free limit
CANCELED paid plan   -> Free limit
```

Existing properties are never deleted when an allowance decreases.

Recurring Stripe invoice outcomes are stored as `SubscriptionPayment` records.

Relevant subscription events include:

- `checkout.session.completed`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.paid`
- `invoice.payment_failed`

Stripe event IDs are persisted once through the shared `StripeEvent` table.

## Plan Management

Default plans:

```text
FREE      2 properties
STANDARD 10 properties
PRO      unlimited
```

Admins can manage pricing, limits, display order, and availability.

## AI Architecture

The AI feature provides operational intelligence rather than a standalone chatbot.

For an authorized property or unit, the backend collects bounded maintenance and expense context and sends it to Gemini.

Structured output contains:

```text
finding
qualification
recommendation
explanation
evidence[]
```

Evidence is restricted to supplied maintenance and expense records, and every evidence ID is validated before persistence.

## AI Reliability Controls

- structured Pydantic output
- output-token limit
- provider timeout
- request rate limiting
- duplicate-running-job protection
- bounded lookback and record counts
- evidence ID/type validation
- property/unit scope validation
- failed-job state
- disabled automatic function calling

AI jobs currently use FastAPI `BackgroundTasks`. A larger system would use a durable queue.

## Database and Migrations

PostgreSQL is the source of truth. SQLAlchemy maps the domain and Alembic manages schema changes.

Production starts with:

```text
alembic upgrade head
```

before Uvicorn.

## CI and Testing

Backend CI uses PostgreSQL 17 and Python 3.13, compiles source, applies all migrations, and runs the full Pytest suite.

Frontend CI uses Node.js 24, `npm ci`, Oxlint, and a Vite production build.

Live Gemini evaluation is deliberately separate from deterministic CI.

## Security Decisions

- secrets live in environment variables
- `.env` files are ignored
- public registration cannot create admins
- role/resource authorization is server-side
- cross-owner and cross-tenant access is rejected
- account suspension is non-destructive
- plan limits are enforced by the backend
- Stripe signatures are required
- browser redirects are non-authoritative
- Stripe event idempotency is persisted
- rent amount/currency/session are validated
- AI context and evidence are validated

## Explicitly Out of Scope

- multi-organization teams
- vendor subsystem
- live-mode/real-money billing
- refunds
- multi-currency accounting
- complex tax handling
- automated lease renewal
- durable distributed workers
- vector databases / RAG
- AI agents
- microservices
- Kubernetes
