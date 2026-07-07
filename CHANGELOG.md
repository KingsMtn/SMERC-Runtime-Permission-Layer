# Changelog

## Unreleased

- Added a developer quickstart for local engine, API, deployment-plan validation, and first-pilot review.
- Added a pilot evaluation checklist and structured JSON checklist for design-partner review.
- Added tests that keep the structured checklist linked to real repository evidence.
- Added a plain-English product overview for nontechnical and CISO-facing review.
- Added a GitHub inspection guide that maps reviewers to the implementation, permits, audit path, deployment adapter, and tests.
- Added a founder explanation card with concise language for applications, customer calls, and design-partner conversations.
- Updated the README and CISO quick review to make the repository easier to understand without a live walkthrough.

## 0.13.0 - 2026-07-05

- Added strict `smerc.execution-plan.v1` and `smerc.execution-report.v1` contracts.
- Added a GitHub deployment adapter that authenticates and atomically reserves one permit before controls, signs control evidence, atomically consumes the reservation, and only then executes a shell-free command.
- Added bounded timeout and cancellation handling, kill escalation, declared rollback, output hashing without raw-output retention, and fail-closed permit-file cleanup.
- Added a separate-authority permit issuer client, composite Action, protected-environment workflow, examples, operations guidance, and adversarial tests.
- Retained explicit limits: the adapter is not a sandbox, control-command success is not independent proof, rollback is not guaranteed restoration, and Windows descendant-process termination requires further hardening.

## 0.12.0 - 2026-07-04

- Added GitHub Actions OIDC verification against GitHub's RS256 JWKS with fixed issuer and `smerc-runtime-api` audience.
- Added exact trust policy for repository and owner IDs, subject, ref, workflow, event, environment, runner class, tenant, and explicit scopes.
- Added atomic one-time source-token exchange registration and `github_oidc.exchanged` audit events without token retention.
- Added `smerc.access-token.v2` workload context binding while retaining verification compatibility for unexpired v1 sessions.
- Added OIDC mode to the GitHub Action, real-GitHub-token container CI, schemas, examples, deployment configuration, and operations guidance.
- Retained explicit limits: GitHub identity does not prove workflow safety, actor intent, runner integrity, or action truthfulness; SQLite replay and JWKS caching remain single-instance pilot controls.

## 0.11.0 - 2026-07-04

- Added `smerc.access-token.v1` short-lived workload sessions with fixed issuer/audience and a 15-minute maximum lifetime.
- Added static-only token exchange, explicit scope narrowing, wildcard removal, session-aware principal attribution, and issuance security events.
- Added signing-key configuration, claims schema, example, deployment and operations guidance, and fail-closed tests.
- Retained explicit limits: no federation, refresh, remote revocation, exchange rate limiting, or managed key lifecycle.

## 0.10.0 - 2026-07-04

- Added signed `smerc.control-evidence.v1` receipts bound to tenant, executor audience, adapter, permit, action hash, applied controls, native references, and freshness.
- Added fail-closed evidence verification for configured adapters and explicit `legacy_caller_assertion` labeling for compatibility paths.
- Added bounded audit attribution, receipt digests, schema, example, deployment configuration, operations guidance, and tests.
- Repaired the permit tampering test so it always mutates significant signature data.

## 0.9.0 - 2026-07-04

- Added tenant-scoped workload principals with explicit evaluation, read, permit, review, metrics, and audit scopes.
- Bound authenticated principal identity into decisions, replay records, and immutable reviews.
- Added attributed security events for permit issuance, permit consumption, and review recording.
- Added fail-closed scope enforcement, cross-principal idempotency protection, legacy-key compatibility, schemas, deployment guidance, and tests.

## 0.8.0 - 2026-07-03

- Added signed `smerc.permit.v1` capabilities bound to tenant, audience, action hash, replay, active policy, controls, and expiry.
- Restricted permit issuance to `ALLOW` and `THROTTLE` decisions under evidence-authorized `ENFORCE` policies.
- Added one-per-decision/audience issuance registration, token-digest matching, atomic one-time consumption, and replay rejection.
- Added permit API endpoints, schema, example action, security boundaries, operating guidance, and tests.

## 0.7.0 - 2026-07-03

- Added tenant-scoped, versioned runtime policy bundles with deterministic policy hashes in decisions and replay records.
- Added evidence-ceiling, fail-behavior, threshold-coherence, and effective-revision safeguards.
- Added append-only SHA-256 and HMAC-SHA-256 evidence provenance ledgers.
- Added provenance-derived deployment caps, schemas, examples, documentation, API configuration, and tests.

## 0.6.0 - 2026-07-02

- Added an executable Evidence and Unknowns Program covering eight core product, safety, integration, authority, performance, and commercial assumptions.
- Added strict evidence-program and observation validation with sample-size, source-quality, and segment requirements.
- Added evidence-derived deployment ceilings from `STOP` through `CALIBRATED_ENFORCE`.
- Added synthetic contradiction examples, schemas, tests, security guidance, and report generation.

## 0.5.0 - 2026-06-30

- Added strict `smerc.action.v1` and `smerc.decision.v1` machine-readable contracts.
- Added deterministic action hashing, structured reasons and controls, and measurable posture-transition conditions.
- Added authenticated `POST /v1/language/evaluate` with tenant-scoped persistence and endpoint-bound idempotency.
- Added JSON Schemas, a production database example, specification, and contract/API tests.

## Unreleased - Pilot Evidence Collection

- Added immutable, tenant-scoped reviewer annotations for replayed decisions.
- Added agreement, override, false-release, false-constraint, useful-constraint, and latency metrics with explicit denominators.
- Added JSON and Markdown pilot metrics export.
- Expanded API validation and automated coverage for review conflicts, retry safety, tenant isolation, and metric interpretation.
- Added a tenant-scoped pending/reviewed decision queue endpoint.
- Added a dependency-free pilot review console for replay inspection, immutable verdict submission, metrics display, and JSON export.
- Added JavaScript model tests and frontend security-contract tests.

## 0.1.0 - External Review Edition

- Added Python runtime permission reference engine.
- Added GitHub Actions integration with observe, recommend, and enforce modes.
- Added example AI-agent action requests.
- Added automated tests.
- Added security, deployment, architecture, CISO, and pilot documentation.
- Published limitations and evidence still required before production enforcement.

## 0.2.0 - Financial Action Governance Profile

- Added the exploratory SMERC-F financial action-governance profile.
- Added structured treasury, settlement, collateral, stablecoin, counterparty, market, model, and agent signals.
- Added synthetic financial action examples and deterministic tests.
- Clarified that SMERC-F is not a token, trading system, custody platform, or production financial control.

## 0.3.0 - Policy Calibration And Audit

- Added conservative, balanced, and permissive financial policy profiles.
- Added deterministic decision hashes tied to action inputs and policy versions.
- Added tamper-evident decision and accountable override audit records.
- Added policy comparison metrics and generated reports.
- Added policy-aware replay and expanded automated validation to 29 tests.

