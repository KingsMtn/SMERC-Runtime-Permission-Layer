# SMERC Product Build Map

## Product Thesis

SMERC is a recoverability-aware runtime permission layer for AI-agent and automated actions. It does not replace IAM, policy engines, code review, SIEM, EDR, or deployment approvals. It adds a pre-execution signal:

> Is this action recoverable enough to execute now?

## Current Product Components

### 1. Recoverability Engine

File: `reference_engine/recoverability_engine.py`

Purpose:

- score irreversible exposure
- score reversible capacity
- score cancel reliability
- score operational stress
- return a runtime posture
- return an enforcement state
- produce reason codes, controls, summary, and replay record

Primary output states:

- `ALLOW`
- `THROTTLE`
- `FREEZE`
- `DENY`
- `ESCALATE`

Enforcement states:

- `release`
- `constrain`
- `pause`
- `block`
- `review`

### 2. API Vehicle

File: `api_server.py`

Endpoints:

- `GET /health`
- `GET /ready`
- `GET /schema`
- `POST /v1/evaluate`
- `POST /v1/batch`
- `GET /v1/decisions`
- `GET /v1/decisions/{replay_id}`

The API uses only the Python standard library so a reviewer can run it without a dependency stack. Pilot controls include tenant-mapped bearer keys, idempotency, bounded requests, allowlisted CORS, and structured errors.

### 3. Pilot Audit Store

File: `reference_engine/audit_store.py`

Purpose:

- persist tenant-scoped decisions
- replay retry-safe decisions by idempotency key
- retrieve individual decision evidence
- list posture-filtered audit summaries
- expose storage readiness

SQLite is intentionally scoped to a single-instance pilot. It is not presented as the final enterprise storage architecture.

### 4. GitHub Actions Gate

Folder: `integrations/github_actions/`

Purpose:

- run SMERC inside GitHub Actions
- support observe, recommend, and enforce modes
- write a decision report artifact
- publish posture, score, and replay ID as step outputs

### 5. Evidence Generators

Files:

- `reference_engine/pilot_report.py`
- `reference_engine/recoverability_report.py`

Purpose:

- evaluate synthetic pilot scenarios
- generate markdown and JSON evidence bundles
- show what a design partner would receive after a shadow-mode pilot

### 6. Deployment Profile

Files:

- `render.yaml`
- `Dockerfile`
- `docker-compose.yml`
- `requirements.txt`

Purpose:

- let a platform reviewer deploy the API with Docker or Render
- define health, secrets, bounded requests, and a persistent pilot audit volume

## What This Build Proves

- The scoring engine runs.
- The API can authenticate, evaluate, persist, replay, and retrieve tenant-scoped decisions.
- The GitHub Actions integration can run in observe, recommend, or enforce mode.
- The repo includes repeatable tests.
- The evidence workflow produces report artifacts.

## What This Build Does Not Prove

- It does not prove production safety.
- It does not prove calibrated enterprise thresholds.
- It does not prove willingness to pay.
- It does not prove the model improves decisions against live workflow data.
- It does not replace existing security controls.

## Next Product Layer

The next layer should be a design-partner pilot that collects:

- reviewer agreement rate
- false release rate
- false freeze / false constraint rate
- override rate
- latency impact
- useful constraint rate
- examples where existing controls allowed an action but SMERC recommended constraint or review
