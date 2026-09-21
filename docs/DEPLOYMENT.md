# PropertyOps Deployment and Operations

This document describes the production deployment topology, environment variables, release process, verification steps, and operational troubleshooting for PropertyOps.

## Production Topology

```text
Frontend        Vercel
Backend         Render
Database        Neon PostgreSQL
Payments        Stripe test mode
AI              Gemini
Source control  GitHub
CI              GitHub Actions
```

The final production branch is `main`.

## Render Backend

**Root directory**

```text
backend
```

**Build command**

```bash
pip install -r requirements.txt
```

**Start command**

```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Health endpoint**

```text
https://propertyops-api-1du2.onrender.com/health
```

Expected:

```json
{"status":"ok"}
```

## Neon PostgreSQL

Use a SQLAlchemy Psycopg connection string:

```text
postgresql+psycopg://USER:PASSWORD@HOST/DATABASE
```

The production database URL must be stored only in Render environment variables.

## Backend Environment Variables

```env
DATABASE_URL=postgresql+psycopg://...
TEST_DATABASE_URL=

FRONTEND_ORIGIN=https://YOUR_PUBLIC_VERCEL_DOMAIN
FRONTEND_URL=https://YOUR_PUBLIC_VERCEL_DOMAIN

JWT_SECRET_KEY=secure-random-production-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_CURRENCY=usd

GEMINI_API_KEY=...
GEMINI_MODEL=gemini-3.5-flash-lite
AI_MAX_RECORDS_PER_TYPE=30
AI_REQUESTS_PER_HOUR=5
AI_LOOKBACK_DAYS=365
AI_TIMEOUT_SECONDS=30
```

`FRONTEND_ORIGIN` must exactly match the active public frontend origin. `FRONTEND_URL` is used for Stripe success/cancel redirects.

## Vercel Frontend

This repository is a monorepo.

When Vercel builds from the repository root, use:

```text
Install Command: npm --prefix frontend ci
Build Command: npm --prefix frontend run build
Output Directory: frontend/dist
```

Frontend environment variable:

```env
VITE_API_URL=https://propertyops-api-1du2.onrender.com/api
```

Vite injects environment variables at build time, so changing the API URL requires a redeploy.

## SPA Routing

The root `vercel.json` rewrites frontend routes to `index.html` so React Router routes continue to work after a direct refresh.

Verify refresh behavior for paths such as:

```text
/app/overview
/app/properties
/app/rent
```

## Vercel Deployment Protection

Preview/branch deployments may require Vercel authentication. The final production domain must be public.

Verify the final production URL from:

- Incognito/private browsing
- A browser not signed into Vercel
- Another device when practical

## Stripe Webhook

Production test-mode webhook endpoint:

```text
https://propertyops-api-1du2.onrender.com/api/stripe/webhook
```

Subscribed events:

```text
checkout.session.completed
checkout.session.expired
payment_intent.payment_failed
```

The webhook signing secret begins with `whsec_` and must be stored in Render as `STRIPE_WEBHOOK_SECRET`.

### End-to-End Payment Verification

1. Tenant starts Checkout.
2. Stripe accepts the test payment.
3. Stripe sends `checkout.session.completed`.
4. Render verifies the signature.
5. Payment becomes `PAID`.
6. Rent obligation becomes `PAID`.
7. Tenant payment history shows `PAID`.
8. Owner payment activity shows `PAID`.

A successful browser redirect alone is not considered proof of payment.

### Stripe Test Card

```text
4242 4242 4242 4242
```

Use any future expiry date and valid test CVC.

## Gemini Production Configuration

Required values:

```env
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-3.5-flash-lite
AI_MAX_RECORDS_PER_TYPE=30
AI_REQUESTS_PER_HOUR=5
AI_LOOKBACK_DAYS=365
AI_TIMEOUT_SECONDS=30
```

Production smoke test: request one authorized property/unit analysis and confirm the job reaches `COMPLETED` with a persisted insight and evidence.

Manual evaluation suite:

```powershell
python -m evals.run_ai_evals
```

## CI

Workflow:

```text
.github/workflows/ci.yml
```

Expected backend regression:

```text
53 passed
```

Expected frontend checks:

```powershell
npm run lint
npm run build
```

## Release Procedure

```text
chore/configure-ci
        |
        v
development
        |
        v
main
        |
        +--> Render
        +--> Vercel
```

Before merging to `main`:

1. Run backend tests.
2. Run frontend lint.
3. Run frontend build.
4. Confirm CI is green.
5. Confirm `.env` is not tracked.
6. Review migrations.

After merging to `main`:

1. Switch Render to deploy from `main`.
2. Switch Vercel production branch to `main`.
3. Verify backend health.
4. Verify public frontend access.
5. Verify owner login/workflow.
6. Verify tenant login/workflow.
7. Verify route refresh.
8. Verify Stripe Checkout + webhook.
9. Verify one AI analysis.
10. Update README with the permanent public frontend URL.
11. Delete obsolete branches only after the final production verification.

## Production Smoke Test

### Infrastructure
- Render is Live
- `/health` returns `ok`
- Neon persists data
- Alembic succeeds
- Vercel is Ready
- Public frontend does not require Vercel login

### Authentication
- Owner can register/login
- Tenant can login
- Logged-out protected routes are blocked
- Tenant cannot access owner-only pages

### Owner
- Property/building/unit data loads
- Tenants/leases load
- Maintenance loads
- Expenses load
- Rent obligations load
- Payments load
- AI insight loads

### Tenant
- Active home/lease loads
- Rent obligations load
- Payment history loads
- Maintenance loads

### Payments
- Checkout opens
- Test payment succeeds
- Webhook succeeds
- Payment becomes `PAID`
- Rent obligation becomes `PAID`

### AI
- Analysis starts
- Job completes
- Insight persists
- Evidence is visible and valid

## Troubleshooting

### CORS/API errors

Verify:

```text
VITE_API_URL
FRONTEND_ORIGIN
FRONTEND_URL
```

### Vercel nested route returns 404

Verify the root `vercel.json` is included in the deployed branch.

### Stripe payment remains PROCESSING

Check:

1. Stripe test mode matches the API key.
2. `checkout.session.completed` is subscribed.
3. Webhook URL is correct.
4. `STRIPE_WEBHOOK_SECRET` matches the deployed endpoint.
5. Stripe delivery status.
6. Render webhook logs.

### AI job fails

Check the Gemini API key, configured model, provider quota, timeout settings, Render logs, and whether enough operational history exists.

## Logs and Observability

Render logs are the primary production diagnostic surface for the current scope.

A larger deployment should add centralized structured logging, error monitoring, metrics, alerting, and background-job monitoring.

## Rollback

For application regressions:

1. Identify the last known-good commit.
2. Revert or redeploy that revision.
3. Do not blindly reverse destructive migrations.
4. Verify database compatibility.
5. Re-run the production smoke test.

Forward-fixing migrations is preferred over unsafe destructive downgrades.

## Secret Handling

Never commit database credentials, JWT secrets, Stripe keys, Stripe webhook secrets, Gemini keys, or real `.env` files.

If a secret is exposed, rotate it immediately.

## Current Backend URLs

```text
API:     https://propertyops-api-1du2.onrender.com
Health:  https://propertyops-api-1du2.onrender.com/health
Swagger: https://propertyops-api-1du2.onrender.com/docs
```

The permanent frontend URL should be finalized after the cutover to `main`.
