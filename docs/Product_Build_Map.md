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
- `GET /schema`
- `POST /evaluate`
- `POST /batch`

The API uses only the Python standard library so a reviewer can run it without a dependency stack.

### 3. GitHub Actions Gate

Folder: `integrations/github_actions/`

Purpose:

- run SMERC inside GitHub Actions
- support observe, recommend, and enforce modes
- write a decision report artifact
- publish posture, score, and replay ID as step outputs

### 4. Evidence Generators

Files:

- `reference_engine/pilot_report.py`
- `reference_engine/recoverability_report.py`

Purpose:

- evaluate synthetic pilot scenarios
- generate markdown and JSON evidence bundles
- show what a design partner would receive after a shadow-mode pilot

### 5. Deployment Profile

Files:

- `render.yaml`
- `requirements.txt`

Purpose:

- let a platform reviewer deploy the API on Render
- define health check and start command

## What This Build Proves

- The scoring engine runs.
- The API can evaluate one action or a batch.
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
