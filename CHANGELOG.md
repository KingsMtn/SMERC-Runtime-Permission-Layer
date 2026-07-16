# Changelog

## Unreleased

- Added a Model and Agent Fitness Layer that scores candidate executors by task fit, data boundary, tool authority, recoverability, reliability history, cost, and latency before selecting an execution posture.
- Added model and agent routing examples, documentation, CLI support, and tests.
- Added `smerc.beacon.v1`, a machine-readable public discovery manifest for agents, tools, reviewers, and search systems, with validation and overclaim checks.
- Added `smerc.agent_handshake.v1`, a reference protocol connecting beacon discovery, agent declaration, executor fitness, recoverability scoring, controls, and replay.
- Added authenticated `POST /v1/agent/handshake` runtime API support with tenant policy evaluation, scoped authorization, schema discovery, security-event logging, and API tests.
- Added Python and JavaScript SDK helpers for calling authenticated agent handshakes.
- Added a generic Agent Handshake integration runner that maps SMERC postures into safe agent-runner states without executing actions.
- Added an OpenAPI 3.1 pilot API contract with endpoint-coverage tests against the server discovery schema.
- Added scoring-invariant verification for recoverability and Model/Agent Fitness math, including generated JSON/Markdown reports and tests.
- Added a CISO evidence walkthrough seed command, realistic seed action set, walkthrough documentation, and tests for review queue plus DLL evidence package readiness.
- Added a CISO evidence package panel to the dependency-free pilot console for stored DLL package generation, JSON export, and Markdown export.
- Added Python and JavaScript SDK helpers for retained DLL storage, stored certificate issuance, and pilot evidence package generation.
- Added pilot evidence package generation from stored DLL records for CISO review.
- Added API issuance of Decision Certificates directly from stored pilot DLL records.
- Added pilot-grade durable Decision Lifecycle Ledger storage with tenant-scoped store, list, and retrieve APIs.
- Added stateless API issuance for pilot Decision Certificates from supplied DLL evidence.
- Added Decision Certificate v1 for digest-bound summaries of verified Decision Lifecycle Ledgers, with optional HMAC signing and SPARTa route binding.
- Added stateless API endpoints for pilot DLL evidence intake and DLL metrics reporting, with authenticated tenant checks and API tests.
- Added pilot ledger metrics that summarize completed DLL evidence with reviewer, execution, outcome, rollback, learning, denominator, and sample-size caveat reporting.
- Added a pilot ledger intake path that appends reviewer, execution, outcome, and learning evidence to existing DLL records while enforcing lifecycle ordering and evidence boundaries.
- Added a benchmark decision-time ledger builder that converts runtime benchmark decisions into hash-chained DLL records while explicitly preserving execution and outcome evidence gaps.
- Added an expanded runtime governance benchmark suite that deterministically expands seed proxy scenarios, compares SMERC postures with allow/deny policy, generates JSON/Markdown evidence reports, and tests proxy-evidence limits.
- Added a SMERC-F profile packet generator with signal taxonomy, multi-policy financial-action evaluation, generated reports, documentation, and commercial-limit tests.
- Added a CISO 30-minute review package and structured checklist that guide a security reviewer through claim, action boundary, recoverability, controls, replayability, and pilot decision evidence.
- Added a replayable governance report generator that assembles SMERC decision, SPARTa route, control mapping, and DLL artifacts into one CISO-readable review package with cross-checks and explicit limits.
- Added a SMERC control mapping library with strict schema, GitHub Actions example mappings, CLI report generation, documentation, and tests for missing or unsupported native controls.
- Added optional HMAC-signed SPARTa route reports with verification, a signed route example, documentation, and tamper-detection tests.
- Added the SMERC Decision Lifecycle Ledger with a strict append-only hash chain, lifecycle event contract, example report, documentation, schema, CLI, and tests.
- Added a Level 5 pilot-readiness maturity model, machine-readable readiness gates, generated readiness report, shadow-mode pilot packet, and tests that verify required evidence links exist.
- Added the first SPARTa posture-aware router, adapter registry, authenticated route API endpoint, example tool plans, route reports, specification, operations guide, CLI, and fail-closed tests.
- Added strict `smerc.domain_profile.v1` custom profile loading for the recoverability engine, CLI, and API server.
- Added recoverability-engine domain profiles, score-contribution trace, posture-threshold trace, and transition guidance.
- Added community and partner materials covering design-partner pilots, integration partners, research reviewers, contribution paths, outreach language, issue templates, and pull-request claims checks.
- Added a proxy incident-replay benchmark with structured scenarios, report generation, summary metrics, demo-ready examples, and explicit production-validation limits.
- Added a dependency-free JavaScript SDK for health, schema, evaluation, Action Language evaluation, batch decisions, replay, reviews, pilot metrics, review queue, security events, permit calls, and short-lived token exchange.
- Added JavaScript SDK quickstart documentation and Node test coverage.
- Added a dependency-free Python SDK for health, schema, evaluation, Action Language evaluation, batch decisions, replay, reviews, pilot metrics, review queue, security events, and permit API calls.
- Added Python SDK quickstart documentation and live API client tests.
- Added starter `smerc.spl.v0` policy-language profile, compiler, example policy, specification, and tests.
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

