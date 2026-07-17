# SMERC External Review Start Here

## Purpose

This page is the first stop for people evaluating SMERC from the public GitHub repository.

SMERC is runtime permission infrastructure for AI-agent and automation actions. It evaluates a proposed action before execution and returns a replayable posture:

- `ALLOW`
- `THROTTLE`
- `FREEZE`
- `DENY`
- `ESCALATE`

The current review question is narrow:

> Is SMERC credible enough to test in a bounded shadow-mode pilot against real AI-agent or automation workflows?

The current review question is not:

> Is SMERC already a production-certified security platform?

## What Exists Now

The repository contains working product artifacts, not only concept documents:

- Python recoverability and runtime permission engine
- versioned action, decision, policy, permit, control-evidence, and DLL contracts
- authenticated REST API
- tenant-scoped audit store
- immutable pilot review records
- denominator-aware pilot metrics
- browser-based pilot review console
- stored Decision Lifecycle Ledger evidence package generation
- Python and JavaScript SDK helpers
- GitHub Actions observe-mode integration
- GitHub deployment adapter with permit reservation, control evidence, timeout, cancellation, rollback, and non-secret reports
- SPARTa posture-aware routing layer
- control mapping library
- replayable governance report generator
- synthetic/proxy benchmark and evidence reports
- tests covering the engine, API, SDKs, console, permits, control evidence, DLL, SPARTa, and GitHub integrations

## What Is Not Claimed

SMERC does not currently claim:

- production certification
- compliance attestation
- proven live incident reduction
- replacement of IAM, OPA, SIEM, EDR, code review, or existing approval systems
- managed enterprise SSO/RBAC
- managed KMS/HSM-backed key lifecycle
- independent attestation that downstream native controls truly executed
- multi-region replay prevention
- customer-validated pricing or demand

Those are validation and productization requirements, not claims in this repository.

## Which Path Should You Use?

| Reviewer | Start Here | Goal |
| --- | --- | --- |
| CISO or security executive | `docs/CISO_30_Minute_Review_Package.md` | Decide whether a shadow-mode pilot is worth discussing. |
| Security architect | `docs/CISO_GitHub_Inspection_Guide.md` | Inspect action boundary, scoring, permits, controls, and audit path. |
| Platform engineer | `docs/CISO_Evidence_Walkthrough.md` and `docs/Developer_Quickstart.md` | Run the seeded evidence flow, engine, API, tests, and GitHub integration locally. |
| Design partner | `pilot_package/Level_5_Shadow_Mode_Pilot_Packet.md` | Understand pilot scope, stop conditions, and evidence required. |
| Open-source reviewer | `CONTRIBUTING.md` and `docs/Public_Review_And_Feedback.md` | Challenge assumptions, scenarios, and implementation details. |
| YC or startup reviewer | `docs/Plain_English_Product_Overview.md` and `docs/Founder_Explanation_Card.md` | Understand the product wedge without overreading the technical material. |

## Recommended 15-Minute Review

1. Read `docs/Public_Review_Snapshot.md`.
2. Read `docs/Plain_English_Product_Overview.md`.
3. Read `docs/CISO_Quick_Review.md`.
4. Inspect `reference_engine/recoverability_engine.py`.
5. Inspect `api_server.py`.
6. Read `docs/CISO_GitHub_Inspection_Guide.md`.
7. Review the latest GitHub Actions test status.

## Recommended 30-Minute Technical Review

1. Follow `docs/CISO_30_Minute_Review_Package.md`.
2. Run `docs/CISO_Evidence_Walkthrough.md`.
3. Run `python -m unittest discover -s tests`.
4. Run one recoverability example from `examples/recoverability_single_action.json`.
5. Inspect the GitHub Actions integration in `integrations/github_actions/`.
6. Inspect the deployment adapter in `integrations/github_deployment/`.
7. Inspect the pilot console in `pilot_console/`.

## Pilot Path

The recommended first pilot is a GitHub Actions shadow-mode pilot:

1. Observe: score proposed actions without blocking existing workflows.
2. Recommend: show posture, reason codes, controls, and reviewer guidance.
3. Enforce selectively only after reviewer agreement and operational thresholds support it.

Useful pilot files:

- `pilot_package/Level_5_Shadow_Mode_Pilot_Packet.md`
- `docs/Pilot_Evaluation_Checklist.md`
- `docs/Pilot_Review_Metrics.md`
- `pilot_console/README.md`
- `docs/API_Deployment_Guide.md`

## Evidence Boundary

The synthetic and proxy reports are useful for product inspection, repeatable testing, and pilot planning. They are not customer evidence.

The project should move from review to stronger claims only after a real pilot produces:

- decision volume across real workflows
- reviewer agreement rate
- false release rate
- false constraint rate
- useful constraint rate
- approval latency impact
- override analysis
- integration burden
- security review findings
- operational incident or near-miss correlation where available

## Bottom Line

SMERC is ready for external technical review and bounded shadow-mode pilot discussion.

SMERC should not be represented as production-certified, compliance-attested, or proven to reduce incidents until real external pilot evidence supports those claims.
