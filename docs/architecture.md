# PayPilot Architecture

```text
User
  |
  v
React UI
  |
  v
FastAPI Orchestrator
  |
  +--> Buyer Agent
  +--> Seller Agents
  +--> Negotiation Agent
  +--> Risk Guardian
  +--> Verification Agent
  |
  +--> Payment Policy Engine
  |       |
  |       +--> ALLOW / BLOCK / HUMAN_APPROVAL
  |
  +--> PayPal Service
  |       +--> Orders API
  |       +--> Authorize
  |       +--> Capture
  |       +--> Webhook Verification
  |
  v
PostgreSQL
  |
  +--> Audit Log
  +--> Payments
  +--> Transactions
  +--> Agent Runs
  |
  v
AG Grid / AG Studio Command Center
```

The financial authority boundary is deliberately outside the LLM.
