# PropertyOps

**Production-style property operations platform with verified payments, recurring subscriptions, and evidence-grounded AI insights.**

PropertyOps is a full-stack application for rental property owners, tenants, and a platform administrator. It combines portfolio management, tenants and leases, automated rent schedules, maintenance, expenses and financial reporting, rent payments, recurring subscription billing, PDF receipts, and structured AI operational intelligence.

The system is implemented as a modular monolith with strict backend authorization, PostgreSQL persistence, signed Stripe webhooks, event idempotency, automated testing, CI, and production deployment.

## Live Application

- **Frontend:** https://propertyops-sz.vercel.app
- **Backend health:** https://propertyops-api-1du2.onrender.com/health
- **API documentation:** https://propertyops-api-1du2.onrender.com/docs

> Stripe runs in test mode. The deployed application is intended for demonstration and evaluation.

## Highlights

- `ADMIN`, `OWNER`, and `TENANT` roles
- Owner-isolated Property → Building → Unit hierarchy
- Tenant provisioning and historical lease management
- Automatic monthly rent obligations from lease terms
- Maintenance workflow with enforced transitions
- Property expenses plus owner-level general operating expenses
- Financial overview: rent collected, expenses, net cash flow, outstanding rent
- Stripe Checkout for tenant rent payments
- Owner-recorded cash rent payments
- Downloadable PDF rent receipts
- FREE / STANDARD / PRO owner plans
- Stripe recurring owner subscriptions
- Backend-enforced property limits
- Admin owner, plan, subscription, and subscription-payment views
- Signed Stripe webhook verification and event idempotency
- Property- and unit-scoped Gemini analysis with validated evidence
- PostgreSQL + SQLAlchemy + Alembic
- GitHub Actions CI
- Vercel + Render + Neon deployment

## Technology Stack

### Frontend
React, TypeScript, Vite, Tailwind CSS, React Router, Recharts, Lucide React, SweetAlert2, Oxlint.

### Backend
Python 3.13, FastAPI, SQLAlchemy 2, Pydantic 2, Alembic, PostgreSQL, JWT, Argon2, Stripe SDK, ReportLab, Google Gen AI SDK.

### Production Services
Vercel, Render, Neon, Stripe test mode, Gemini, GitHub Actions.

## Roles

### Admin
Admins can review platform owner usage, deactivate/reactivate owner access, manage plans, review subscriptions, and review recurring subscription payments.

Admin accounts are provisioned separately; public registration cannot create an admin.

### Owner
Owners can manage properties/buildings/units, tenants, leases, maintenance, expenses, financial reporting, rent obligations and payments, cash payments, PDF receipts, AI analysis, and their PropertyOps subscription.

### Tenant
Tenants can view their active home and lease, owner contact information, unpaid rent, payment history, PDF receipts, and maintenance requests. Tenants can pay rent through Stripe Checkout.

## Rent and Payment Model

Lease creation generates monthly rent obligations using a calendar-month anchor. Paid rent is retained in history; ending or shortening a lease only cancels applicable future pending obligations.

```text
Lease
  |
  v
Monthly Rent Obligations
  |
  +--> Stripe Checkout --> verified webhook --> PAID
  |
  +--> Owner records cash -------------------> PAID
```

Browser redirects are never treated as proof of payment.

## Subscription Billing

Default plans:

| Plan | Monthly | Yearly | Property limit |
| --- | ---: | ---: | ---: |
| FREE | $0 | $0 | 2 |
| STANDARD | $9 | $90 | 10 |
| PRO | $19 | $190 | Unlimited |

Paid plan limits are granted only when Stripe-backed subscription status is `ACTIVE`. `INCOMPLETE`, `PAST_DUE`, and `CANCELED` paid subscriptions fall back to the Free-plan property limit without deleting existing properties.

Rent and subscription traffic share one signed Stripe webhook endpoint and are separated with metadata:

```text
flow=RENT
flow=SUBSCRIPTION
```

## Financial Overview

Owners can review rent collected, property and general expenses, net cash flow, outstanding rent, and income-vs-expense trends using monthly, 30-day, yearly, or custom date ranges.

## AI Property Intelligence

The AI feature is integrated into property operations rather than implemented as a standalone chatbot.

PropertyOps sends bounded maintenance and expense context for an authorized property or unit. Gemini returns structured findings with qualification, explanation, recommendation, and evidence references.

Evidence IDs are validated against the exact records supplied before persistence.

Safeguards include context limits, rate limiting, provider timeout, structured output validation, evidence validation, property/unit scope checks, and failed-job handling.

## Local Development

### Backend

```powershell
git clone https://github.com/SirineZamzam/PropertyOps-DH.git
cd PropertyOps-DH\backend

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env

alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```powershell
cd ..\frontend
npm ci
npm run dev
```

Frontend `.env`:

```env
VITE_API_URL=http://127.0.0.1:8000/api
```

## Environment Variables

```env
DATABASE_URL=postgresql+psycopg://...
TEST_DATABASE_URL=

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

Never commit real secrets.

## Testing

Backend:

```powershell
cd backend
python -m compileall app
alembic upgrade head
python -m pytest tests -q
```

Frontend:

```powershell
cd frontend
npm ci
npm run lint
npm run build
```

Live Gemini evaluation is intentionally separate from deterministic CI:

```powershell
cd backend
python -m evals.run_ai_evals
```

## CI

Backend CI uses PostgreSQL 17 and Python 3.13, compiles backend source, runs Alembic migrations, and executes the full Pytest suite.

Frontend CI uses Node.js 24, runs `npm ci`, Oxlint, and the Vite production build.

Workflow: `.github/workflows/ci.yml`

## Production

| Component | Service |
| --- | --- |
| Frontend | Vercel |
| Backend | Render |
| Database | Neon PostgreSQL |
| Payments | Stripe test mode |
| AI | Gemini |
| CI | GitHub Actions |

Production URLs:

- https://propertyops-sz.vercel.app
- https://propertyops-api-1du2.onrender.com
- https://propertyops-api-1du2.onrender.com/health
- https://propertyops-api-1du2.onrender.com/docs

See `docs/ARCHITECTURE.md` and `docs/DEPLOYMENT.md`.

## Security and Reliability

PropertyOps includes password hashing, JWT authentication, role-based authorization, cross-owner and cross-tenant protection, account deactivation without destructive deletion, backend property-limit enforcement, signed Stripe webhooks, event idempotency, payment validation, subscription state verification, AI evidence validation, bounded AI context, migrations, regression tests, and CI.

## Architectural Tradeoffs

PropertyOps intentionally uses a modular monolith rather than premature microservices.

AI jobs use FastAPI `BackgroundTasks`, which is appropriate for this project scope but is not a durable job queue.

Stripe remains in test mode so the system demonstrates real hosted payments and recurring billing without processing real customer funds.

## Author

**Sirine Zamzam**

Software Engineer focused on full-stack and backend systems.
