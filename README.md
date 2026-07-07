# SMERC Runtime Permission Layer

[![Tests](https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/actions/workflows/tests.yml/badge.svg)](https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/actions/workflows/tests.yml)

## External Technical Review Edition

SMERC is runtime permission infrastructure for AI-agent actions. It evaluates a proposed action before execution and returns a replayable posture:

- `ALLOW`
- `THROTTLE`
- `FREEZE`
- `DENY`
- `ESCALATE`

The first integration is a GitHub Actions gate for AI-assisted code, deployment, and infrastructure workflows.

The current build includes:

- versioned SMERC Action Language and Decision Language contracts
- evidence and unknowns registry with deployment-limiting falsification rules
- tenant-scoped policy calibration and evidence provenance admission
- signed, action-bound, single-use authorization permits
- signed, action-bound control-evidence receipts for configured execution adapters
- scoped workload principals with proposer, issuer, executor, reviewer, and auditor separation
- short-lived, scope-narrowed workload sessions issued from static pilot principals
- GitHub Actions OIDC verification with repository-, workflow-, ref-, environment-, and run-bound attribution
- recoverability-aware scoring engine
- authenticated, tenant-scoped REST API service
- SQLite pilot audit store with idempotent decision replay
- immutable pilot review records and denominator-aware metrics
- dependency-free pilot review console
- GitHub Actions gate
- local and authenticated remote GitHub Action evaluation
- permit-consuming GitHub deployment adapter with native controls, cancellation, rollback, and non-secret execution reports
- synthetic shadow-mode scenario packs
- evidence/report generators
- Render deployment profile

## Why This Repository Exists

This public repository is the external technical review edition of SMERC. It contains the implementation and documentation needed for a security, platform, or product team to determine whether SMERC is worth testing in shadow mode.

It intentionally excludes private legal drafts, patent strategy, competition submissions, investor materials, outreach records, and internal commercial planning.

## If You Are New To SMERC

Start here before reading the code:

- `docs/Plain_English_Product_Overview.md` explains what SMERC does, what exists now, and what is not proven yet.
- `docs/CISO_GitHub_Inspection_Guide.md` shows what a security or platform reviewer should inspect first.
- `docs/Founder_Explanation_Card.md` gives a short nontechnical explanation for founder calls, YC-style applications, and design-partner conversations.
- `docs/Developer_Quickstart.md` gives technical reviewers a short run-and-inspect path.
- `docs/Pilot_Evaluation_Checklist.md` and `examples/pilot_evaluation_checklist.json` give design partners a concrete evaluation checklist.
- `specification/SMERC_SPL_v0.md` introduces a starter policy-language profile that compiles to the strict runtime policy contract.

The shortest accurate explanation is:

> SMERC helps companies decide whether AI-agent and automation actions are recoverable enough to execute now.

## Review In 10 Minutes

1. Read `docs/Plain_English_Product_Overview.md`.
2. Read `docs/CISO_GitHub_Inspection_Guide.md`.
3. Read `docs/Developer_Quickstart.md`.
4. Read `docs/Pilot_Evaluation_Checklist.md`.
5. Read `docs/CISO_Quick_Review.md`.
6. Read `docs/Security_Model.md`.
7. Inspect `reference_engine/recoverability_engine.py`.
8. Inspect `reference_engine/action_language.py` and `specification/SMERC_Action_Language_v1.md`.
9. Read `docs/Policy_Calibration_And_Evidence_Provenance.md`.
10. Inspect `api_server.py` and `reference_engine/audit_store.py`.
11. Review `integrations/github_actions/README.md`.
12. Read `docs/Pilot_Review_Metrics.md`.
13. Inspect `pilot_console/README.md`.
14. Inspect `reference_engine/authorization_permit.py` and `specification/SMERC_Action_Bound_Permit_v1.md`.
15. Read `docs/Scoped_Workload_Identity.md`.
16. Inspect `reference_engine/control_evidence.py` and `specification/SMERC_Control_Evidence_v1.md`.
17. Read `docs/Short_Lived_Access_Operations.md` and `specification/SMERC_Access_Token_v2.md`.
18. Read `docs/GitHub_OIDC_Operations.md` and `specification/SMERC_GitHub_OIDC_Trust_v1.md`.
19. Inspect `integrations/github_deployment/` and read `docs/GitHub_Deployment_Adapter_Operations.md`.
20. Run the Python and console tests.
21. Review `pilot_package/SMERC_Shadow_Mode_Pilot_One_Pager.md`.

## What SMERC Evaluates

The reference engine accepts structured action metadata:

- action identity and description
- tool and actor
- confidence
- harm potential
- consent or authorization support
- reversibility
- external side effects
- sensitive-data involvement
- optional context

It outputs:

- runtime posture
- risk score
- confidence score
- reason codes
- recommended constraints
- policy identity, revision, mode, evidence ceiling, and hash
- replay ID and replay record
- an optional short-lived permit for eligible enforcement decisions
- authenticated principal identity bound into decisions, replays, reviews, and security events
- signed control-evidence attribution when configured at permit consumption

## Action Language

`smerc.action.v1` is the machine-readable boundary between an agent proposing an action and SMERC deciding its runtime posture. It separates action identity, authority, risk signals, recoverability, effects, and bounded replay context. `smerc.decision.v1` returns structured reasons, controls, and measurable transition conditions alongside the existing scores and replay record.

This is the practical meaning of Macro Language Model in the current product: SMERC does not generate micro-level content. It provides a versioned macro-level vocabulary for whether automated action may proceed, under what constraints, and what evidence is needed before a posture can change.

```bash
python -m reference_engine.action_language examples/action_language/production_database_change.json
```

Schemas and full semantics are in `schemas/` and `specification/SMERC_Action_Language_v1.md`.

## SMERC Policy Language

`smerc.spl.v0` is a starter policy-language profile for pilot review. It gives reviewers a human-oriented way to define tenant, mode, evidence ceiling, and posture thresholds, then compiles into the existing strict `smerc.policy.v1` runtime contract.

```bash
python -m reference_engine.spl examples/policies/github_actions_shadow_spl.json --pretty
python -m reference_engine.spl examples/policies/github_actions_shadow_spl.json --hash
```

SPL v0 is deliberately narrow. It is not yet a full policy language with grammar tooling, imports, IDE support, or formal verification. See `specification/SMERC_SPL_v0.md`.

## Action-Bound Permits

An eligible `smerc.decision.v1` result can be converted into a signed `smerc.permit.v1` capability for the exact original action. The permit binds the authenticated tenant, intended executor, action hash, replay ID, active policy hash, required controls, and a lifetime of no more than five minutes.

Permits are deliberately narrow:

- only an evidence-authorized `ENFORCE` policy may issue one
- only `ALLOW` and `THROTTLE` decisions qualify
- `THROTTLE` carries constraints into the execution boundary
- one decision may issue one permit per executor audience
- consumption is atomic and single use in the pilot store
- preparation authenticates and reserves one permit before native controls can run
- policy replacement, action mutation, wrong audience, expiry, missing controls, or replay causes rejection

The token is not exposed by the GitHub Action because it is a bearer capability. Executors obtain and consume it through the authenticated API. See `docs/Action_Bound_Permit_Operations.md`.

## Verifiable Control Evidence

Configured execution adapters first authenticate and reserve a permit, then replace caller-supplied control names with short-lived `smerc.control-evidence.v1` receipts. Each receipt is signed by a key scoped to one tenant and executor audience and binds the adapter, permit, action hash, applied controls, native mechanisms, evidence references, and observation times.

This improves authenticity, freshness, and auditability; it does not prove a compromised adapter or key is truthful. Unconfigured audiences retain a migration-only path labeled `legacy_caller_assertion`. See `docs/Control_Evidence_Operations.md`.

## Scoped Workload Identity

New pilots can assign separate tenant credentials to the action proposer, permit issuer, permit consumer, reviewer, decision reader, metrics reader, and auditor. Unauthorized endpoint use fails with `insufficient_scope`; authenticated principal identity is preserved in decisions and security events.

Legacy `SMERC_API_KEYS` remain compatible and retain all tenant scopes. New non-federated deployments should use `SMERC_API_PRINCIPALS` for separation of duties. Static credentials remain a pilot compatibility model. GitHub Actions may instead use the bounded OIDC path described below. See `docs/Scoped_Workload_Identity.md`.

## Short-Lived Workload Sessions

When `SMERC_ACCESS_TOKEN_KEY` is configured, a static principal can exchange its bootstrap credential for a `smerc.access-token.v2` session lasting no more than 15 minutes. The session can only preserve or narrow the principal's explicit scopes; it cannot use wildcard authority or mint another session. Decisions retain the session ID and expiry. The verifier remains compatible with unexpired v1 sessions.

This reduces routine exposure of static credentials but does not prove workload identity or replace federated IAM. See `docs/Short_Lived_Access_Operations.md`.

## GitHub Actions OIDC

When `SMERC_GITHUB_OIDC_TRUST` is configured, a GitHub Actions job can exchange GitHub's signed OIDC identity for a workload-bound SMERC session without storing `SMERC_API_KEY`. SMERC verifies the GitHub signature, fixed issuer and audience, time window, and exact configured repository, immutable IDs, subject, ref, workflow ref and commit SHA, event, environment, and runner class. The source token is exchangeable once in the pilot audit store.

The resulting decision records verified repository, workflow, commit, run, actor, and environment context. This proves signed GitHub claims, not workflow safety or authorization by itself. See `docs/GitHub_OIDC_Operations.md`.

## Quick Start

Requires Python 3.10 or later. No third-party Python packages are required.

```bash
python -m reference_engine.agent_permission_layer examples/agent_permission_actions.json --pretty
python -m reference_engine.recoverability_engine examples/recoverability_single_action.json --pretty
python -m unittest discover -s tests
```

Validate a deployment plan without issuing permission or executing its command:

```bash
python integrations/github_deployment/deployment_adapter.py \
  --action-file examples/action_language/production_canary_release.json \
  --plan-file examples/github_deployment/execution_plan.json \
  --mode validate
```

The enforce path requires separate proposer, issuer, executor, and control-evidence authorities. See `integrations/github_deployment/README.md`; do not substitute the public simulation commands for a reviewed deployment procedure.

Run the recoverability API locally without authentication only for development:

```bash
python api_server.py --host 127.0.0.1 --port 8788 --audit-db :memory: --allow-unauthenticated
```

Then call:

```bash
curl http://127.0.0.1:8788/health
curl -X POST http://127.0.0.1:8788/evaluate -H "Content-Type: application/json" --data @examples/recoverability_single_action.json
```

Run authenticated pilot mode with durable local audit records:

```bash
export SMERC_API_PRINCIPALS="pilot-team:pilot-console:actions.evaluate+decisions.read+reviews.read+reviews.write+metrics.read=development-console-secret-2026-rotate"
export SMERC_AUDIT_DB="./smerc_audit.sqlite3"
python api_server.py --host 127.0.0.1 --port 8788

curl -X POST http://127.0.0.1:8788/v1/evaluate \
  -H "Authorization: Bearer development-console-secret-2026-rotate" \
  -H "Idempotency-Key: workflow-run-1001" \
  -H "Content-Type: application/json" \
  --data @examples/recoverability_single_action.json
```

Evaluate the versioned action contract through the authenticated API:

```bash
curl -X POST http://127.0.0.1:8788/v1/language/evaluate \
  -H "Authorization: Bearer development-console-secret-2026-rotate" \
  -H "Idempotency-Key: language-run-1001" \
  -H "Content-Type: application/json" \
  --data @examples/action_language/production_database_change.json
```

Pilot API controls include scoped tenant principals, tenant-scoped audit retrieval, principal-bound idempotent replay, optional action-bound permit issuance and consumption, immutable reviewer annotations, body and batch limits, allowlisted CORS, liveness/readiness endpoints, and structured request IDs. See `docs/API_Deployment_Guide.md` and `docs/Pilot_Review_Metrics.md`.

After a decision is reviewed, record the pseudonymous reviewer outcome and retrieve pilot metrics:

```bash
curl -X POST "http://127.0.0.1:8788/v1/decisions/$REPLAY_ID/reviews" \
  -H "Authorization: Bearer development-console-secret-2026-rotate" \
  -H "Idempotency-Key: review-$REPLAY_ID-security-1" \
  -H "Content-Type: application/json" \
  --data @examples/pilot_review.json

curl "http://127.0.0.1:8788/v1/pilot/metrics" \
  -H "Authorization: Bearer development-console-secret-2026-rotate"
```

Rates are returned with denominators and remain `null` when not measurable. They describe reviewed pilot records only; they are not production accuracy claims.

Run the browser-based pilot review console:

```bash
export SMERC_CORS_ORIGINS="http://127.0.0.1:8790"
python -m http.server 8790 --bind 127.0.0.1 --directory pilot_console
```

Open `http://127.0.0.1:8790` and connect it to the authenticated API. The bearer key remains in memory for that tab; the console uses no browser storage, cookies, analytics, or third-party assets. See `pilot_console/README.md`.

Run the GitHub Actions gate locally:

```bash
python integrations/github_actions/run_smerc_gate.py \
  --action-file integrations/github_actions/sample_action_request.json \
  --mode observe \
  --output-file smerc-decision.json
```

The GitHub Action can also call the authenticated `/v1/evaluate` endpoint. Remote mode supports an exact GitHub OIDC trust policy or the static `SMERC_API_KEY` compatibility path, requires HTTPS outside loopback tests, reuses an idempotency key across evaluation retries, and fails closed in enforce mode. See `integrations/github_actions/README.md`.

Generate a synthetic GitHub Actions shadow-mode pilot report:

```bash
python -m reference_engine.pilot_report \
  examples/github_actions_shadow_mode_scenarios.json \
  --json-output reports/github_actions_shadow_mode_results.json \
  --markdown-output reports/GitHub_Actions_Shadow_Mode_Pilot_Report.md
```

Generate a recoverability-engine evidence report:

```bash
python -m reference_engine.recoverability_report \
  examples/recoverability_action_requests.json \
  --json-output reports/recoverability_engine_results.json \
  --markdown-output reports/Recoverability_Engine_Report.md
```

Evaluate the core assumptions against currently admitted evidence:

```bash
python -m reference_engine.evidence_program \
  examples/evidence_program/core_assumptions.json \
  examples/evidence_program/no_observations.json \
  --json-output reports/evidence_readiness_baseline.json \
  --markdown-output reports/SMERC_Evidence_Readiness_Baseline.md
```

With no qualified observations, the evidence engine limits deployment to `OBSERVE`. A challenged critical claim forces `STOP`. See `docs/Evidence_And_Unknowns_Program.md`.

Bind decisions to a calibrated tenant policy and verify evidence provenance:

```bash
python -m reference_engine.recoverability_engine \
  examples/recoverability_single_action.json \
  --policy examples/policies/alpha_conservative.json \
  --pretty

python -m reference_engine.evidence_provenance build \
  examples/evidence_program/synthetic_observations.json \
  examples/evidence_program/synthetic_artifact_digests.json \
  reports/synthetic_evidence_ledger.json \
  --program-id smerc-core-validation-v1 \
  --collector-id synthetic-collector \
  --collection-method synthetic-demonstration
```

See `docs/Policy_Calibration_And_Evidence_Provenance.md` for policy activation, provenance strength, HMAC use, and limitations.

Run the optional SMERC-F financial action-governance profile:

```bash
python -m reference_engine.financial_permission_profile \
  examples/financial_action_requests.json --policy balanced --pretty
```

Run the SMERC-F historical-context replay suite:

```bash
python -m reference_engine.financial_replay \
  examples/financial_replay_scenarios.json \
  --report reports/SMERC_F_Replay_Report.md
```

## GitHub Actions Modes

| Mode | Behavior |
| --- | --- |
| `observe` | Score and report; never fail the workflow. |
| `recommend` | Surface posture and constraints for reviewer use. |
| `enforce` | Fail selected high-risk postures after calibration and approval. |

The recommended first deployment is `observe` mode.

## What SMERC Is Not

- Not a replacement for IAM, OPA, branch protection, code review, SIEM, or existing approvals.
- Not a prompt-injection filter.
- Not a production-certified security platform.
- Not a claim that current thresholds are already calibrated for every enterprise.
- Not intended to receive production secrets, raw customer data, or full private prompts in a first pilot.
- Not a cryptocurrency, token, trading system, custody platform, or financial product.

## Optional Domain Profile

`SMERC-F` demonstrates how the core permission engine can govern proposed treasury, settlement, liquidity, collateral, and tokenized-finance actions. It is explicitly labeled exploratory and uses synthetic examples.

See `docs/SMERC_Financial_Action_Governance.md`.

Replay method and limitations are documented in `docs/SMERC_F_Replay_Validation.md`.

Policy calibration, deterministic hashes, accountable overrides, and tamper-evident audit records are documented in `docs/SMERC_F_Policy_And_Audit.md`.

## Public Review Links

- CISO review: https://admirable-sorbet-9986d5.netlify.app/ciso.html
- Interactive demo: https://admirable-sorbet-9986d5.netlify.app
- GitHub Actions pilot: https://admirable-sorbet-9986d5.netlify.app/github-action.html
- Pilot options: https://admirable-sorbet-9986d5.netlify.app/pilot.html

## Current Evidence

- Working Python reference engine
- Recoverability-focused scoring engine
- Standard-library REST API service
- Signed action-bound permit contract with single-use pilot consumption
- Signed adapter control-evidence receipts with permit, action, and freshness binding
- Scoped workload principals and attributed security-event audit records
- Short-lived, scope-narrowed workload sessions with issuance attribution
- GitHub Actions OIDC exchange with exact trust policy and one-time source-token replay prevention
- Browser-based pilot review queue and metrics console
- Installable local GitHub Action
- Deterministic example action requests
- GitHub Actions shadow-mode scenario pack
- Generated pilot-style evidence report
- Automated tests
- Security and deployment documentation
- Render deployment profile
- Public interactive demo
- Defined shadow-mode pilot

See `reports/GitHub_Actions_Shadow_Mode_Pilot_Report.md` for the current synthetic pilot report. It is not customer evidence; it shows the report shape a design partner should expect after live workflow scoring.

See `reports/Recoverability_Engine_Report.md` for the current recoverability-engine report.

See `docs/Product_Build_Map.md` and `docs/API_Deployment_Guide.md` for the current product architecture and deployment path.

## Evidence Still Required

- live workflow pilot data
- reviewer agreement and override rates
- false release and false constraint measurements
- threshold calibration against customer workflows
- latency and operational impact measurements
- production security and legal review

## Pilot Question

> Does recoverability-aware runtime scoring change reviewer judgment in a useful and repeatable way before AI-agent actions create side effects?

SMERC should be adopted only if a controlled pilot produces evidence that the answer is yes.

## License

See `LICENSE`.
