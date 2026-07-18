# SMERC Product Build Map

## Product Thesis

SMERC is a recoverability-aware runtime permission layer for AI-agent and automated actions. It does not replace IAM, policy engines, code review, SIEM, EDR, or deployment approvals. It adds a pre-execution signal:

> Is this action recoverable enough to execute now?

## Current Product Components

### 1. Action And Decision Language

File: `reference_engine/action_language.py`

Purpose:

- validate strict `smerc.action.v1` envelopes
- compile agent and workflow proposals into engine inputs
- create deterministic action hashes for replay comparison
- return structured reasons, controls, and posture-transition conditions
- preserve compatibility with the recoverability engine and audit store

This is the stable integration boundary. It turns SMERC's vocabulary into an executable contract instead of relying on prose or integration-specific field mappings.

### 2. Recoverability Engine

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

### 3. API Vehicle

File: `api_server.py`

Endpoints:

- `GET /health`
- `GET /ready`
- `GET /schema`
- `POST /v1/evaluate`
- `POST /v1/language/evaluate`
- `POST /v1/batch`
- `GET /v1/decisions`
- `GET /v1/decisions/{replay_id}`
- `POST /v1/decisions/{replay_id}/reviews`
- `GET /v1/decisions/{replay_id}/reviews`
- `GET /v1/pilot/metrics`
- `GET /v1/review-queue`

The API uses only the Python standard library so a reviewer can run it without a dependency stack. Pilot controls include scoped tenant principals, principal-bound idempotency, bounded requests, allowlisted CORS, and structured errors.

### 4. Pilot Audit Store

File: `reference_engine/audit_store.py`

Purpose:

- persist tenant-scoped decisions
- replay retry-safe decisions by idempotency key
- retrieve individual decision evidence
- list posture-filtered audit summaries
- persist immutable, pseudonymous reviewer annotations
- calculate agreement, override, false-release, false-constraint, useful-constraint, and latency metrics
- expose storage readiness

SQLite is intentionally scoped to a single-instance pilot. It is not presented as the final enterprise storage architecture.

### 5. Pilot Review Console

Folder: `pilot_console/`

Purpose:

- connect to an authenticated pilot API without persisting the bearer key
- filter pending and reviewed tenant decisions
- inspect replay scores, reason codes, controls, and prior reviews
- submit immutable pseudonymous reviews
- display and download denominator-aware pilot metrics

The console is a pilot operator surface. It does not provide production identity, RBAC, or enforcement controls.

### 6. GitHub Actions Gate

Folder: `integrations/github_actions/`

Purpose:

- run SMERC inside GitHub Actions
- support bundled local evaluation and authenticated remote API evaluation
- support observe, recommend, and enforce modes
- write a decision report artifact
- publish posture, score, and replay ID as step outputs
- preserve idempotency across remote retries
- fail closed on remote-service unavailability in enforce mode

### 7. Evidence Generators

Files:

- `reference_engine/pilot_report.py`
- `reference_engine/recoverability_report.py`
- `reference_engine/pilot_metrics_report.py`

Purpose:

- evaluate synthetic pilot scenarios
- generate markdown and JSON evidence bundles
- export denominator-aware pilot review metrics
- show what a design partner would receive after a shadow-mode pilot

### 8. Evidence And Unknowns Program

File: `reference_engine/evidence_program.py`

Purpose:

- register technical, adversarial, operational, normative, commercial, and regulatory unknowns
- define falsifiable thresholds before observing outcomes
- reject underpowered, low-quality, or incorrectly segmented observations
- lower the deployment ceiling when critical evidence is missing or contradictory
- generate JSON and Markdown readiness reports

The program does not certify safety. It prevents unresolved assumptions from being hidden by implementation progress.

### 9. Policy Calibration And Evidence Provenance

Files:

- `reference_engine/policy.py`
- `reference_engine/evidence_provenance.py`

Purpose:

- bind every decision and replay to an exact tenant policy revision and hash
- prevent policy mode from exceeding the admitted evidence ceiling
- activate the latest effective tenant revision without early activation or silent fallback
- detect mutated, missing, duplicated, or reordered evidence observations
- cap deployment based on provenance strength

Hash-chain provenance detects mutation but does not establish source truth. HMAC mode provides shared-key authenticity, not public nonrepudiation.

### 10. Deployment Profile

Files:

- `render.yaml`
- `Dockerfile`
- `docker-compose.yml`
- `requirements.txt`

Purpose:

- let a platform reviewer deploy the API with Docker or Render
- define health, secrets, bounded requests, and a persistent pilot audit volume

### 11. Action-Bound Authorization Permits

Files:

- `reference_engine/authorization_permit.py`
- `schemas/smerc-action-bound-permit-v1.schema.json`

Purpose:

- convert eligible enforcement decisions into short-lived signed capabilities
- bind authorization to the exact tenant, executor audience, action, replay, policy, and constraints
- reject altered, expired, wrong-audience, superseded-policy, and replayed permits
- carry `THROTTLE` controls to the execution boundary
- register one issuance per decision/audience, reserve it for one execution, and atomically consume it once

The pilot uses tenant HMAC keys and SQLite replay state. This proves the execution contract, not production key management, workload identity, distributed replay prevention, independent verification of native control operation, or nonrepudiation.

### 12. Scoped Workload Identity

Files:

- `reference_engine/api_identity.py`
- `schemas/smerc-authenticated-principal-v1.schema.json`
- `schemas/smerc-security-event-v1.schema.json`

Purpose:

- separate action proposers, permit issuers, permit consumers, reviewers, readers, and auditors
- deny endpoint operations when the authenticated principal lacks the required scope
- bind authenticated principal identity into decisions, replays, and reviews
- append tenant-scoped security events for permit issuance, permit consumption, and review recording
- preserve legacy all-scope keys for controlled compatibility

This begins with static bearer-secret pilot principals and can derive expiring, scope-narrowed sessions. GitHub Actions can additionally use provider-specific OIDC trust. General enterprise federation, managed rotation/revocation, and external immutable audit storage remain outside the reference build.

### 13. Signed Control Evidence

Files:

- `reference_engine/control_evidence.py`
- `schemas/smerc-control-evidence-v1.schema.json`
- `specification/SMERC_Control_Evidence_v1.md`

Purpose:

- replace caller-supplied control names with signed adapter receipts when configured
- bind adapter, permit, action, tenant, audience, controls, native references, and freshness
- reject failed, stale, altered, missing, wrong-action, wrong-audience, and wrong-permit evidence
- retain receipt digests and bounded attribution without storing bearer tokens
- preserve an explicitly labeled compatibility path for unconfigured pilot audiences

HMAC authenticates the configured pilot adapter key but does not independently prove that the adapter or referenced native mechanism is truthful. Production needs managed workload identity, protected signing, native evidence verification, and external audit.

### 14. Short-Lived Workload Sessions

Files:

- `reference_engine/access_token.py`
- `schemas/smerc-access-token-v1.schema.json`
- `schemas/smerc-access-token-v2.schema.json`
- `specification/SMERC_Access_Token_v1.md`
- `specification/SMERC_Access_Token_v2.md`

Purpose:

- exchange a static bootstrap credential for a session lasting at most 15 minutes
- preserve tenant and principal while allowing only equal or narrower explicit scopes
- prevent wildcard sessions and session-to-session token minting
- bind session ID and expiry into authenticated principal attribution
- record issuance metadata without retaining bearer tokens

Static exchange reduces repeated secret exposure but does not prove the external workload. V2 can additionally carry context supplied by a verified federation boundary.

### 15. GitHub Actions OIDC Trust

Files:

- `reference_engine/github_oidc.py`
- `schemas/smerc-github-oidc-trust-v1.schema.json`
- `specification/SMERC_GitHub_OIDC_Trust_v1.md`
- `docs/GitHub_OIDC_Operations.md`

Purpose:

- verify GitHub's RS256 OIDC signature and fixed issuer/audience
- require exact repository, immutable IDs, subject, ref, workflow, event, environment, and runner policy
- exchange each source token once for a narrower SMERC session
- bind repository, workflow, commit, run, actor, and environment context into decisions
- remove stored `SMERC_API_KEY` from the configured Actions evaluation path

This proves a bounded GitHub workload identity claim, not the safety of its workflow, runner, actor, or proposed action. SQLite replay state and process-local JWKS caching remain single-instance pilot controls.

### 16. GitHub Deployment Execution Adapter

Files:

- `integrations/github_deployment/deployment_adapter.py`
- `integrations/github_deployment/issue_permit.py`
- `integrations/github_deployment/action.yml`
- `schemas/smerc-execution-plan-v1.schema.json`
- `schemas/smerc-execution-report-v1.schema.json`
- `schemas/smerc-sparta-execution-evidence-v1.schema.json`

Purpose:

- require an action-bound permit before a declared side effect
- map every permit-required control to a successful native command or internal cancellation mechanism
- authenticate and reserve the permit before controls, then sign control evidence and atomically consume the reservation before execution
- verify supplied SPARTa route-to-permit binding before command execution
- execute argument arrays without shell interpretation
- terminate timed-out or cancelled processes and attempt declared rollback
- produce a hash- and status-based report without raw output, secrets, or tokens

This creates an executable pilot lifecycle, not a sandbox or production-certified deployment controller. Native control commands, runner integrity, descendant-process handling, external state restoration, and multi-instance replay prevention remain validation and hardening requirements.

## What This Build Proves

- The scoring engine runs.
- The API can authenticate, evaluate, persist, replay, retrieve, and review tenant-scoped decisions.
- Pilot metrics preserve explicit denominators and null values when evidence is insufficient.
- The review console can exercise the review and metrics workflow without third-party frontend dependencies.
- The GitHub Actions integration can run in observe, recommend, or enforce mode.
- The repo includes repeatable tests.
- The evidence workflow produces report artifacts.
- The evidence registry converts unresolved assumptions into enforceable deployment ceilings.
- Tenant decisions carry replayable policy identity, while evidence provenance limits how far observations may advance deployment.
- Eligible enforcement decisions can produce action-bound permits that a named executor verifies and consumes once.
- Scoped principals prevent a proposing agent from automatically inheriting permit-issuance or execution authority.
- Configured adapters must provide signed, fresh control evidence bound to the exact action and permit.
- Configured principals can use expiring, scope-narrowed sessions without expanding authority.
- The GitHub deployment adapter can order native controls, one-time permit consumption, bounded execution, cancellation, rollback attempt, and non-secret reporting in one tested path.
- The fake AcmeCloud production-like test can exercise safe, constrained, blocked, review-required, and rollback paths with valid Decision Lifecycle Ledger chains.
- The real public incident replay can run public postmortem-derived scenarios through SMERC while preserving the source-fact versus analyst-assigned-signal boundary.

## What This Build Does Not Prove

- It does not prove production safety.
- It does not prove calibrated enterprise thresholds.
- It does not prove willingness to pay.
- It does not prove the model improves decisions against live workflow data.
- It does not turn synthetic evidence into customer or production validation.
- It does not replace existing security controls.
- It does not prove process isolation, native-control truth, guaranteed rollback, or production runner integrity.

## Next Product Layer

The implemented review layer is ready for a design-partner pilot to collect:

- reviewer agreement rate
- false release rate
- false freeze / false constraint rate
- override rate
- latency impact
- useful constraint rate
- examples where existing controls allowed an action but SMERC recommended constraint or review

The software can collect these measurements; only a real pilot can determine whether they support the product thesis.
