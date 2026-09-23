# PropertyOps Deployment and Operations

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

Production branch:

```text
main
```

## Production URLs

```text
Frontend:
https://propertyops-sz.vercel.app

Backend:
https://propertyops-api-1du2.onrender.com

Health:
https://propertyops-api-1du2.onrender.com/health

Swagger:
https://propertyops-api-1du2.onrender.com/docs

Stripe webhook:
https://propertyops-api-1du2.onrender.com/api/stripe/webhook
```

## Render Backend

Root directory:

```text
backend
```

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Render Environment

```env
DATABASE_URL=postgresql+psycopg://...
TEST_DATABASE_URL=

FRONTEND_ORIGIN=https://propertyops-sz.vercel.app
FRONTEND_URL=https://propertyops-sz.vercel.app

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

Do not add a trailing slash to `FRONTEND_ORIGIN` or `FRONTEND_URL`.

## Vercel Frontend

Monorepo commands:

```text
Install Command:
npm --prefix frontend ci

Build Command:
npm --prefix frontend run build

Output Directory:
frontend/dist
```

Production environment variable:

```env
VITE_API_URL=https://propertyops-api-1du2.onrender.com/api
```

The root `vercel.json` handles SPA rewrites.

## Stripe Production-Test Webhook

Endpoint:

```text
https://propertyops-api-1du2.onrender.com/api/stripe/webhook
```

Keep the rent-related events:

```text
checkout.session.completed
checkout.session.expired
payment_intent.payment_failed
```

Add subscription events:

```text
customer.subscription.created
customer.subscription.updated
customer.subscription.deleted
invoice.paid
invoice.payment_failed
```

The signing secret for this exact endpoint must be stored in Render as:

```text
STRIPE_WEBHOOK_SECRET
```

Do not use a Stripe CLI `whsec_...` value in production.

The shared webhook distinguishes flows with:

```text
flow=RENT
flow=SUBSCRIPTION
```

## Production Admin Provisioning

Public registration cannot create an admin.

After production migrations finish, create the one admin from the Render service shell:

```bash
python -m scripts.create_admin   --email "admin@propertyops.dev"   --password "<PRIVATE_PRODUCTION_ADMIN_PASSWORD>"   --first-name "PropertyOps"   --last-name "Admin"
```

Use a private password that is not stored in the repository.

## Final Local Release Checks

Backend:

```powershell
cd backend

python -m compileall app
alembic heads
alembic current
python -m pytest tests -q
```

Frontend:

```powershell
cd ..\frontend

npm run lint
npm run build
```

Repository:

```powershell
cd ..
git diff --check
git status
```

## Release Procedure

### 1. Final branch

Complete regression and documentation on:

```text
chore/final-regression-production
```

Commit and push.

### 2. Development

Merge the final branch into `development`.

Push and verify GitHub Actions is green.

### 3. Main

Merge `development` into `main`.

Push and verify GitHub Actions on `main`.

### 4. Render / Neon

Render deploys `main`.

Watch the deploy logs and confirm Alembic completes before Uvicorn starts.

Health must return:

```json
{"status":"ok"}
```

### 5. Vercel

Confirm production deploy uses `main`.

Verify the frontend in an incognito/private browser.

### 6. Stripe

Confirm the test-mode webhook has all rent + subscription events enabled and recent deliveries return successful responses.

### 7. Admin

Provision the production admin if one does not already exist.

### 8. Smoke tests

Run the checklist below.

## Production Smoke Tests

### Infrastructure

- Render service is Live
- `/health` returns `ok`
- `/docs` opens
- production migrations completed
- Vercel deployment is Ready
- frontend is public
- nested route refresh works

### Authentication / Authorization

- owner can register
- owner sees plan-choice screen
- owner can login
- tenant can login
- admin can login
- logged-out protected routes are blocked
- tenant cannot enter owner/admin resources
- owner cannot enter admin resources
- admin cannot enter owner-only routes

### Owner

- overview loads
- properties/buildings/units load
- people/leases load
- tenant management loads
- lease creation generates obligations
- maintenance loads
- property expenses work
- general expenses work
- financial overview updates
- rent page loads
- manual cash payment works
- PDF receipt works
- subscription page loads
- plan/usage badge loads

### Tenant

- active home/lease loads
- owner contact displays
- only unpaid obligations are shown
- rent Checkout opens
- verified paid rent appears in history
- PDF receipt downloads
- maintenance creation/tracking works

### Admin

- overview loads
- owners table loads
- plan/status/usage columns load
- owner deactivate/reactivate works
- plans page loads
- subscriptions page loads
- subscription-payment page loads

## Rent Stripe Production Test

1. Use an owner with a tenant and pending obligation.
2. Sign in as the tenant.
3. Start Checkout.
4. Use test card:

```text
4242 4242 4242 4242
```

Use any future expiry and valid test CVC.

5. Complete Checkout.
6. Confirm Stripe delivery succeeds.
7. Confirm payment becomes `PAID`.
8. Confirm obligation becomes `PAID`.
9. Confirm it disappears from unpaid rent.
10. Confirm payment history keeps it.
11. Download the PDF receipt.
12. Confirm owner recent payment activity shows it.

## Subscription Stripe Production Test

Use a fresh owner.

1. Register.
2. Confirm plan selection appears.
3. Choose Standard monthly.
4. Complete Stripe test Checkout.
5. Confirm subscription webhook deliveries succeed.
6. Confirm status becomes `ACTIVE`.
7. Confirm sidebar shows Standard.
8. Confirm Standard property allowance is active.
9. Confirm owner subscription-payment history shows a `PAID` invoice.
10. Confirm Admin → Subscriptions shows `ACTIVE`.
11. Confirm Admin → Subscription payments shows the invoice.
12. Optionally schedule cancellation, then immediately click **Keep subscription** to verify the period-end cancellation toggle without ending the demo subscription.

## Gemini Production Test

1. Use an owner with maintenance/expense history.
2. Request one property or unit analysis.
3. Confirm job reaches `COMPLETED`.
4. Confirm insight persists.
5. Confirm evidence references valid supplied records.

Live evals remain optional:

```powershell
python -m evals.run_ai_evals
```

## Responsive UX

Verify at least:

```text
~390px mobile
~768px tablet
desktop
```

Check sidebar/mobile menu, modals, horizontally scrollable tables, subscription cards, rent/payment screens, and dark mode.

## Troubleshooting

### Render migration failure

Read the exact Alembic/PostgreSQL error before changing production data. Do not manually delete schema objects or stamp revisions blindly.

### Rent remains PROCESSING

Check the test-mode Stripe key, webhook URL, endpoint signing secret, `checkout.session.completed`, Stripe delivery result, and Render logs.

### Subscription remains INCOMPLETE

Check:

```text
customer.subscription.created
customer.subscription.updated
invoice.paid
```

Also inspect Stripe delivery responses, Render logs, and metadata (`flow`, `owner_id`, `plan_id`, `billing_interval`).

### CORS/API errors

Verify:

```text
VITE_API_URL
FRONTEND_ORIGIN
FRONTEND_URL
```

### AI job fails

Check Gemini key/model/quota, timeout settings, operational history, and Render logs.

## Rollback

For an application regression:

1. identify the last known-good commit
2. revert or redeploy application code
3. do not blindly downgrade destructive database migrations
4. verify schema compatibility
5. prefer a forward-fix migration when schema repair is required
6. rerun production smoke tests

## Secret Handling

Never commit database credentials, JWT secrets, Stripe keys, webhook secrets, Gemini keys, or real `.env` files.
