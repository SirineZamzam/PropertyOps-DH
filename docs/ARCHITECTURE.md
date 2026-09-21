# PropertyOps Architecture

This document describes the system design, trust boundaries, domain model, payment workflow, AI workflow, security decisions, and engineering tradeoffs behind PropertyOps.

## Architectural Style

PropertyOps is a **modular monolith**. The frontend and backend are deployed separately, while the backend remains one FastAPI application organized into clear modules for routes, authentication, models, schemas, services, persistence, and integrations.

This approach keeps deployment simple while preserving separation of concerns and a clear path for future scaling.

## Runtime Topology

```text
Browser
  |
  | HTTPS
  v
React / Vite frontend on Vercel
  |
  | REST + JWT
  v
FastAPI backend on Render
  |
  +--> Neon PostgreSQL
  +--> Stripe Checkout / Webhooks
  +--> Gemini API
```

## Trust Boundaries

The frontend is never treated as a security boundary. Authorization is enforced on the backend for every sensitive operation.

The backend validates:

- Authenticated user identity
- OWNER vs TENANT role
- Property ownership
- Building-to-property membership
- Unit-to-building membership
- Lease-to-tenant ownership
- Lease-to-unit membership
- Maintenance scope
- Expense scope
- Rent obligation scope
- Payment scope
- AI property/unit scope

## Core Domain Model

```text
User
 |
 +-- OWNER
 |
 +-- TENANT

OWNER
 |
 +-- Property
      |
      +-- Building
           |
           +-- Unit
                |
                +-- Lease
                     |
                     +-- TENANT
                     +-- RentObligation
                          |
                          +-- Payment
```

Operational entities include `Maintenance`, `Expense`, `StripeEvent`, `AIAnalysisJob`, `AIInsight`, and `AIInsightEvidence`.

## Lease Design

Tenancy is modeled through `Lease` instead of storing a tenant directly on a unit. This preserves history, supports tenant movement between units, and keeps occupancy rules explicit.

The system enforces one active lease per unit.

## Maintenance Workflow

```text
OPEN -> ASSIGNED -> IN_PROGRESS -> RESOLVED
```

Tenants create OPEN requests for their own unit. Owners control subsequent transitions. Invalid transitions are rejected by backend business logic.

## Expense Model

Expenses belong to a property and may optionally reference a unit and/or maintenance record. Cross-property references are rejected to prevent inconsistent data.

## Payment Architecture

The browser redirect after Stripe Checkout is not authoritative. A payment becomes PAID only after a verified Stripe webhook is processed.

```text
Tenant starts checkout
  |
  v
Backend creates Payment(PENDING)
  |
  v
Stripe Checkout Session created
  |
  v
Payment -> PROCESSING
  |
  v
Stripe checkout completed
  |
  v
Signed checkout.session.completed webhook
  |
  v
Verify signature + event idempotency
  |
  v
Verify session + amount + currency + payment status
  |
  v
Payment -> PAID
RentObligation -> PAID
```

Stripe event IDs are persisted to make duplicate webhook deliveries safe.

## AI Architecture

The AI feature is operational intelligence, not a standalone chatbot.

Owners can request analysis for a property or unit. The backend verifies authorization, collects bounded maintenance/expense history, and sends only that operational context to Gemini.

Gemini returns structured output:

```text
finding
qualification
recommendation
explanation
evidence[]
```

Qualification is restricted to `LOW`, `MEDIUM`, or `HIGH`. Evidence is restricted to `MAINTENANCE` and `EXPENSE` records.

Every returned evidence ID is validated against the exact context supplied to the model before persistence. This prevents hallucinated or cross-scope evidence from being saved.

## AI Reliability Controls

- Structured Pydantic response schema
- Low-temperature generation
- Output token limit
- Provider timeout
- Request rate limiting
- Duplicate-running-job protection
- Maximum lookback period
- Maximum records per type
- Evidence ID/type validation
- Property/unit scope validation
- Graceful FAILED job state
- Disabled automatic function calling

## Background Processing

AI jobs use FastAPI `BackgroundTasks`. This is appropriate for the current project scope and avoids a separate queue/worker service.

Tradeoff: `BackgroundTasks` is process-local. A process restart can interrupt an in-flight job. A larger production system would use a durable queue and dedicated worker.

## Authentication

Authentication uses JWTs. Passwords are stored as hashes. OWNER/TENANT authorization is enforced independently of frontend routing.

## Database and Migrations

PostgreSQL is the source of truth. SQLAlchemy models the domain and Alembic manages schema migrations.

Production startup runs:

```text
alembic upgrade head
```

before Uvicorn starts.

## CI Strategy

Backend CI runs PostgreSQL 17, Python 3.13, dependency installation, source compilation, Alembic migrations, and the full Pytest suite.

Frontend CI runs Node.js 24, `npm ci`, Oxlint, and a production Vite build.

The live Gemini evaluation suite is deliberately excluded from CI so CI does not depend on provider availability, secrets, cost, or nondeterministic model behavior.

## Testing Strategy

The backend regression suite contains 53 tests covering authentication, authorization, leases, maintenance, expenses, rent obligations, payments, AI routing, AI persistence, evidence validation, rate limiting, provider failures, and timeouts.

Production regression additionally verifies Vercel SPA routing, Render health, Neon persistence, Stripe Checkout/webhooks, AI analysis, and responsive UX.

## Security Decisions

- Secrets stored in environment variables
- Real `.env` files ignored by Git
- Public registration creates owners only
- Tenants are owner-provisioned
- Cross-owner and cross-tenant access rejected server-side
- Stripe webhook signatures required
- Browser redirect never marks a payment as paid
- Payment session/amount/currency validated
- AI evidence validated before persistence
- AI context deliberately minimized

## Explicitly Out of Scope

- Multi-organization tenancy
- Vendor subsystem
- Subscription billing
- Refund workflows
- Multi-currency
- Complex tax logic
- Automated lease renewal
- Vector databases
- RAG
- AI agents
- Microservices
- Kubernetes

## Future Evolution

Likely next steps at larger scale include a durable worker queue, audit log, notifications, object storage, owner teams, payment reconciliation tools, staging, centralized observability, and backup/restore procedures.
