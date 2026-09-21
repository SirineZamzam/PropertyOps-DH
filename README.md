# PropertyOps

**AI-powered property operations platform for owners and tenants.**

PropertyOps is a production-style full-stack application for managing rental property operations from one place. It combines portfolio management, tenant and lease workflows, maintenance tracking, expenses, rent obligations, Stripe payments, and evidence-grounded AI operational intelligence.

The system is built as a modular monolith with strict server-side authorization, verified Stripe webhooks, structured AI output, PostgreSQL persistence, automated testing, CI, and production deployment.

## Live Application

**Frontend:** https://propertyops-sz.vercel.app

**Backend health:** https://propertyops-api-1du2.onrender.com/health

**API documentation:** https://propertyops-api-1du2.onrender.com/docs

> Stripe is integrated in test mode. The live application is intended for demonstration and evaluation.

## Highlights

- Role-based workflows for **OWNER** and **TENANT**
- Owner-isolated Property → Building → Unit hierarchy
- Tenant provisioning and historical lease management
- One active lease per unit
- Maintenance workflow with enforced transitions
- Property expenses with optional unit/maintenance linkage
- Rent obligations and verified payment history
- Real Stripe Checkout in test mode
- Signed Stripe webhook verification and event idempotency
- Property- and unit-scoped AI analysis
- Structured Gemini output with validated evidence
- AI rate limiting, timeouts, bounded context, and failure handling
- PostgreSQL with SQLAlchemy and Alembic migrations
- 53 backend regression tests
- Frontend lint/build validation
- GitHub Actions CI
- Production deployment with Vercel, Render, Neon, Stripe, and Gemini

## Technology Stack

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- React Router
- Recharts
- Lucide React
- SweetAlert2
- Oxlint

### Backend

- Python 3.13
- FastAPI
- SQLAlchemy 2
- Pydantic 2
- Alembic
- PostgreSQL
- JWT authentication
- Argon2 password hashing
- Stripe SDK
- Google Gen AI SDK

### Production Services

- **Vercel** — frontend hosting
- **Render** — FastAPI backend hosting
- **Neon** — managed PostgreSQL
- **Stripe** — Checkout and signed webhook processing
- **Gemini** — operational intelligence
- **GitHub Actions** — continuous integration

## System Overview

```text
Browser
  |
  v
React / Vite frontend
  |
  | HTTPS + JWT
  v
FastAPI API on Render
  |
  +---------------------> Neon PostgreSQL
  |
  +---------------------> Stripe Checkout
  |                         |
  |                         v
  |                    Signed webhook
  |                         |
  |<------------------------+
  |
  +---------------------> Gemini API
                            |
                            v
                    Structured AI result
                            |
                            v
                  Validation + persistence
```

Authorization and business rules are enforced in the backend. The frontend is responsible for presentation and interaction, while ownership, tenancy, workflow transitions, payment verification, and AI evidence validation remain server-side concerns.

For deeper design details, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Core Domain

```text
Owner
  |
  +-- Property
        |
        +-- Building
              |
              +-- Unit
                    |
                    +-- Lease
                          |
                          +-- Tenant
                          +-- Rent Obligations
```

Operational records include:

- Maintenance
- Expenses
- Payments
- AI analysis jobs
- AI insights
- AI evidence references

Tenants are linked to units through leases rather than directly from the user record. This preserves lease history and keeps occupancy rules explicit.

## User Roles

### Owner

Owners can:

- Manage properties, buildings, and units
- Provision tenant accounts
- Create and manage leases
- Track maintenance
- Move maintenance through valid workflow states
- Record expenses
- Create rent obligations
- Review payment activity
- Request property- or unit-level AI analysis
- Inspect AI findings and supporting evidence

Owner data is isolated by portfolio.

### Tenant

Tenants can:

- Sign in to an owner-provisioned account
- View their active lease and unit
- View rent obligations
- Start Stripe Checkout
- Review verified payment history
- Submit maintenance requests
- Track maintenance status
- Manage profile information

Tenants cannot access owner-only operations or another tenant's resources.

## Maintenance Workflow

```text
OPEN
  |
  v
ASSIGNED
  |
  v
IN_PROGRESS
  |
  v
RESOLVED
```

Invalid transitions are rejected by backend business logic.

## Stripe Payment Flow

PropertyOps does **not** trust the browser redirect as proof of payment.

```text
Tenant selects Pay
  |
  v
Backend creates Payment + Stripe Checkout Session
  |
  v
Payment = PROCESSING
  |
  v
Tenant completes Stripe Checkout
  |
  v
Stripe sends checkout.session.completed
  |
  v
FastAPI verifies Stripe signature
  |
  v
Event idempotency + amount/currency/session validation
  |
  v
Payment = PAID
Rent obligation = PAID
```

Webhook event IDs are persisted so duplicate Stripe deliveries are safely ignored.

## AI Property Intelligence

The AI feature is integrated into the operational workflow rather than implemented as a standalone chatbot.

PropertyOps sends bounded maintenance and expense context for an authorized property or unit. Gemini returns structured output containing:

- Finding
- Qualification: `LOW`, `MEDIUM`, or `HIGH`
- Optional recommendation
- Explanation
- Evidence references

Every evidence ID returned by the model is validated against the exact records supplied to it before persistence.

Safeguards include:

- 12-month maximum lookback
- Record-count limits
- Request rate limiting
- Provider timeout
- Structured schema validation
- Evidence type restrictions
- Evidence ID validation
- Property/unit scope validation
- Failed-job handling
- Disabled automatic function calling
- Output token limits

The live-model evaluation suite is available under `backend/evals`.

## Project Structure

```text
PropertyOps-DH/
|
+-- .github/
|   +-- workflows/
|       +-- ci.yml
|
+-- backend/
|   +-- alembic/
|   +-- app/
|   |   +-- api/
|   |   +-- core/
|   |   +-- db/
|   |   +-- models/
|   |   +-- schemas/
|   |   +-- services/
|   +-- evals/
|   +-- tests/
|   +-- .env.example
|   +-- alembic.ini
|   +-- requirements.txt
|
+-- frontend/
|   +-- src/
|   +-- package.json
|   +-- package-lock.json
|
+-- docs/
|   +-- ARCHITECTURE.md
|   +-- DEPLOYMENT.md
|
+-- README.md
+-- vercel.json
```

## Local Development

### Prerequisites

- Python 3.13+
- Node.js 24+
- PostgreSQL
- Git

### Backend

```powershell
git clone https://github.com/SirineZamzam/PropertyOps-DH.git
cd PropertyOps-DH\backend

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Configure `backend/.env` with local database credentials, a JWT secret, Stripe test credentials, and a Gemini API key.

Run migrations:

```powershell
alembic upgrade head
```

Start the API:

```powershell
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

Health:

```text
http://127.0.0.1:8000/health
```

### Frontend

```powershell
cd ..\frontend
npm ci
```

Create `frontend/.env`:

```env
VITE_API_URL=http://127.0.0.1:8000/api
```

Start the frontend:

```powershell
npm run dev
```

Frontend:

```text
http://localhost:5173
```

## Environment Variables

Backend example:

```env
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/propertyops_db
TEST_DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/propertyops_test_db

FRONTEND_ORIGIN=http://localhost:5173
FRONTEND_URL=http://localhost:5173

JWT_SECRET_KEY=replace-with-secure-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

STRIPE_SECRET_KEY=sk_test_replace_me
STRIPE_WEBHOOK_SECRET=whsec_replace_me
STRIPE_CURRENCY=usd

GEMINI_API_KEY=replace_me
GEMINI_MODEL=gemini-3.5-flash-lite
AI_MAX_RECORDS_PER_TYPE=30
AI_REQUESTS_PER_HOUR=5
AI_LOOKBACK_DAYS=365
AI_TIMEOUT_SECONDS=30
```

Never commit real secrets. `.env` files are Git-ignored.

## Testing

### Backend

From `backend/`:

```powershell
python -m pytest tests -q
```

Current regression suite:

```text
53 passed
```

### AI Evaluation

Run the live-model evaluation suite from `backend/`:

```powershell
python -m evals.run_ai_evals
```

Live Gemini calls are intentionally excluded from CI because CI should not depend on external model availability, secrets, token cost, or nondeterministic provider behavior.

### Frontend

From `frontend/`:

```powershell
npm run lint
npm run build
```

## Continuous Integration

GitHub Actions validates both application halves.

Backend CI:

1. Starts PostgreSQL 17
2. Installs Python dependencies
3. Compiles backend source
4. Runs Alembic migrations
5. Runs backend tests

Frontend CI:

1. Installs Node.js 24
2. Runs `npm ci`
3. Runs Oxlint
4. Builds the Vite production bundle

Workflow: [.github/workflows/ci.yml](.github/workflows/ci.yml)

## Production

| Component | Service |
| --- | --- |
| Frontend | Vercel |
| Backend | Render |
| Database | Neon PostgreSQL |
| Payments | Stripe test-mode Checkout + signed webhook |
| AI | Gemini |
| CI | GitHub Actions |

### Production URLs

- **Application:** https://propertyops-sz.vercel.app
- **Backend health:** https://propertyops-api-1du2.onrender.com/health
- **Swagger:** https://propertyops-api-1du2.onrender.com/docs

Full deployment and operational guidance is documented in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Security and Reliability

PropertyOps includes:

- Password hashing
- JWT authentication
- Role-based authorization
- Cross-owner protection
- Cross-tenant protection
- Server-side workflow validation
- Signed Stripe webhook verification
- Stripe event idempotency
- Payment amount, currency, and session validation
- Secret management through environment variables
- AI schema validation
- AI evidence validation
- AI context limits
- AI rate limiting
- Provider timeout handling
- Database migrations
- Automated regression testing
- CI checks before release

## Architectural Tradeoffs

PropertyOps is intentionally a modular monolith. It avoids premature microservices while preserving clear separation between API routes, models, schemas, services, and external integrations.

AI processing currently uses FastAPI `BackgroundTasks`. This keeps deployment simple and is appropriate for the project scope, but it is not a durable queue. A larger production system would move AI execution to a persistent queue and dedicated worker.

Stripe remains in test mode because the project demonstrates real hosted payment integration without processing real customer funds.

More detail: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Author

**Sirine Zamzam**

Software Engineer focused on full-stack and backend systems.
