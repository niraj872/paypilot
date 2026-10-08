# PayPilot

**AI agents that negotiate, verify, and safely move money for you.**

PayPilot is a competition-grade prototype for agentic commerce: a user describes a real-world task, AI agents compare and negotiate offers, a backend Policy Engine enforces hard financial limits, PayPal Sandbox handles payment authorization/capture, a Verification Agent checks fulfillment, and the dashboard exposes the complete audit trail.

## What is real vs demo

### Real / production-capable paths
- FastAPI REST backend
- PostgreSQL persistence
- PayPal Orders v2 service layer (OAuth, create order, authorize, capture)
- PayPal webhook verification endpoint
- Backend payment policy enforcement
- Idempotency key model
- Agent audit trail
- AG Grid transaction intelligence
- AG Studio embedded analytics integration
- Render deployment configuration

### Simulated in `DEMO_MODE=true`
- Seller marketplace participants
- Seller fulfillment
- Deterministic negotiation responses
- Deterministic verification results
- PayPal API responses are simulated and labeled as demo mode; no claim of real payment is made

For a real PayPal Sandbox demonstration, set `DEMO_MODE=false` and provide PayPal Sandbox credentials in the backend environment.

## Demo story

> “I need a React authentication bug fixed within 24 hours. My maximum budget is $100. Pay only when the work passes verification.”

The platform demonstrates:

1. Buyer Agent parses the task.
2. Seller agents offer price / ETA / quality.
3. Negotiation Agent negotiates within hard user constraints.
4. Risk Guardian scores the payment.
5. Policy Engine allows or blocks the action.
6. PayPal order is created/authorized.
7. Verification Agent validates fulfillment.
8. PayPal capture completes only after successful verification.
9. AG Grid / AG Studio expose transactions, risk and audit data.

## Stack

- Frontend: React + TypeScript + Vite + Tailwind CSS
- Analytics: AG Grid + AG Studio
- Backend: Python + FastAPI + Pydantic
- Database: PostgreSQL + SQLAlchemy
- Payments: PayPal REST Orders v2 / Webhooks
- Deployment: Render
- Containers: Docker Compose

AG Grid's current React install uses `ag-grid-react` / `ag-grid-community`; AG Studio's current React package is `ag-studio-react` with version-matched `ag-studio`. citeturn224665search0turn181284search2

PayPal's current Orders v2 guidance recommends server-side API calls and supports `AUTHORIZE` and later `CAPTURE`; webhook listeners must verify events and return a 2xx response for accepted deliveries. citeturn224665search3turn224665search7

Render supports FastAPI services, Docker, and managed PostgreSQL. citeturn224665search4turn224665search5

## Run locally

### Option A — Docker (recommended)

```bash
docker compose up --build
```

Frontend: http://localhost:5173
Backend: http://localhost:8000
Docs: http://localhost:8000/docs

### Option B — local processes

Start PostgreSQL, then:

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux
python -m uvicorn app.main:app --reload --port 8000
```

Then:

```bash
cd frontend
npm install
npm run dev
```

## Demo API flow

Create task:

```http
POST /api/tasks
Content-Type: application/json

{
  "title": "Fix React Authentication Bug",
  "description": "Fix the React authentication bug and deliver a tested patch.",
  "budget_max": 100,
  "deadline_hours": 24,
  "payment_condition": "release_after_verification",
  "quality_requirement": "tests_pass"
}
```

Run agents:

```http
POST /api/tasks/{id}/run
```

Create PayPal order:

```http
POST /api/payments/create
{"task_id": 1}
```

Capture after successful verification:

```http
POST /api/payments/capture
{"task_id": 1}
```

Failure demos:

```http
POST /api/demo/failure
{"scenario":"budget_exceeded"}
```

```http
POST /api/demo/failure
{"scenario":"verification_failed"}
```

## PayPal Sandbox

Set:

```text
DEMO_MODE=false
PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com
PAYPAL_CLIENT_ID=...
PAYPAL_CLIENT_SECRET=...
PAYPAL_WEBHOOK_ID=...
```

Keep credentials only in your environment / Render secrets. Never commit `.env`.

## AG Studio

The app includes an AG Studio analytics page over transaction data. AG Studio can be tested locally without a production license, while production use without the development watermark requires a trial/production license. The current Studio Agent Framework can be connected to an application-supplied LLM adapter; this repository keeps the data/dashboard layer self-contained so the demo remains deterministic. citeturn181284search0turn181284search3

## Security model

**AI recommends. Backend authorizes. PayPal executes.**

The Policy Engine enforces:

- hard maximum transaction amount
- allowed currency
- risk threshold
- duplicate transaction protection
- verification before capture

The webhook endpoint verifies PayPal signatures when `DEMO_MODE=false` and de-duplicates provider event IDs.

## Tests

```bash
cd backend
pytest
```

Or:

```bash
make test
```

## Full audit

```bash
make audit
```

The audit prints PASS/FAIL checks for the repo structure, backend tests and secret-file hygiene.

## Render deployment

A `render.yaml` Blueprint is included. It provisions:

- FastAPI web service
- React static site
- managed PostgreSQL
- PayPal environment variables as secrets

Render's current documentation supports Python/FastAPI web services, public `onrender.com` URLs, and managed PostgreSQL. citeturn224665search4turn224665search5

After creating the Blueprint, update `CORS_ORIGINS` and `VITE_API_BASE_URL` to your final Render URLs.

## Competition notes

The project is intentionally optimized around one strong end-to-end story instead of a collection of unrelated sponsor demos:

**Understand → Negotiate → Risk Check → PayPal → Verify → Capture → Explain**

AG Grid / AG Studio are used for the transaction intelligence and analytics experience, not merely for a sponsor logo.

## License

MIT
