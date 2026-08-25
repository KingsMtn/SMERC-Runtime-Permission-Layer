# Changelog

## Unreleased

- Added a click-by-click reviewer guide for running the public runtime customer-evaluation workflow from GitHub Actions.
- Added a repository-native Runtime Customer Evaluations GitHub Actions workflow for running the general and financial runtime evaluation examples from the Actions tab.
- Added a Financial Runtime Customer Evaluation pack, internally called SMERC-F, with finance-specific metadata-only actions, reviewer guidance, generated reports, and tests.
- Added a copyable GitHub Actions customer-evaluation workflow that runs the metadata-only customer evaluation package and uploads a review artifact without SMERC API credentials.
- Added a Customer Evaluation runner, sample metadata-only action set, docs, report outputs, and tests for customer-supplied action review before a shadow-mode pilot.
- Added Ref-gated runtime proof output to the one-command reviewer quickstart so reviewers can inspect hard evidence gates, capped scoring, SPARTa routing, DLL evidence, CISO seed evidence, and benchmark results from one generated package.
- Added a Ref-gated runtime proof loop, generated report, tests, documentation, and an OpenSSF issue #50 response draft showing hard mechanical gates before recoverability scoring.
- Added a one-command strategic reviewer evidence packet, strategic reviewer brief, outbound message, and GitHub issue template for large-company/platform review.
- Added strategic acquisition positioning, strategic buyer map, platform-fit rationale, IP asset map, and technical diligence index for large-company review.
- Added an Autonomy Continuance reference engine, example case, CLI, docs, reports, and tests for Authority Provenance, Intent Integrity, Consequence Horizon, Collective Autonomy, and Right To Continue.
- Added an Earned Autonomy reference engine, example agent history, CLI, docs, reports, and tests that convert historical reviewer agreement, overrides, ref-gate failures, rollback results, false releases, incidents, scope violations, and evidence gaps into a starting autonomy tier.
- Added an Autonomy Budgeting reference engine, CLI, docs, reports, and tests that meter current AI-agent freedom by action count, scope units, cumulative risk spend, ref-gate failures, blocked or held attempts, and allowed tool risk tiers.
- Added deterministic ref-gate checks to the MCP Governance Gateway for typed contract validity, attestation validity, least-privilege confirmation, and expected object shape, including fail-closed scoring behavior, example MCP session metadata, generated report fields, documentation, and tests.
- Added an Autonomy Health framework for evaluating whether an AI agent, workflow, or tool family should retain, reduce, suspend, or requalify its level of independence over time.
- Added a CISO/security architect 15-minute review path that routes serious reviewers from product claim to MCP Gateway proof, GitHub Actions pilot path, replay evidence, pilot decision criteria, and explicit non-claim boundaries.
- Added an MCP Governance Gateway that evaluates registry-defined MCP tool-call sessions with repeated-call pressure, scope pressure, session-budget metering, SMERC posture routing, SPARTa route behavior, proxy action recommendations, generated reports, and SMERC-F financial tool-family support.
- Added a SMERC-F metadata intake contract and sample customer template for safe financial-services shadow-mode review without customer records, raw regulated transaction payloads, wallet keys, live fund movement, or production enforcement.
- Added a SMERC-F pilot evidence packet that combines source ingestion, regulatory-context overlay, public replay, reviewer questions, go/no-go criteria, and claim boundaries for financial-services review.
- Added a SMERC-F regulatory context overlay that compares baseline financial replay with legislation-inspired operational metadata without making legal, AML, sanctions, fraud, custody, settlement, or compliance claims.
- Added a SMERC-F financial source ingestion adapter that normalizes Dune-, BigQuery-, Chainabuse-, DefiLlama-, and Elliptic-shaped exported metadata into replay-ready SMERC-F rows and bounded reports.
- Added a SMERC-F financial public-data replay harness that expands Dune-, BigQuery-, Chainabuse-, DefiLlama-, and Elliptic-shaped public records into 50 recoverability-scored financial action scenarios with bounded reports and tests.
- Added a Fortune 500 financial-services review package and checklist for SMERC-F, focusing on metadata-only shadow-mode evaluation of automated financial actions without claiming AML, fraud, custody, settlement, trading, payment execution, or production-certified financial control.
- Added public language and naming guidance so external surfaces lead with familiar category language before internal layer names such as SPARK, SPARTa, and DLL.
- Added cloud automation guardrails positioning for cloud admin, infrastructure-as-code, IAM, Kubernetes, database, deployment, and destructive cloud-resource actions as a searchable next-lane surface for recoverability-aware runtime permissioning.
- Added a Self-Service Pilot Connector that accepts mixed metadata-only GitHub Actions/action-language and MCP transport events, then produces a compact pilot-fit decision package with posture counts, highest exposure events, replay IDs, and recommended next action.
- Added an MCP Transport Proxy sample that accepts a local JSON-RPC-style `tools/call` envelope, routes it through the MCP Proxy Runner, and returns either a forwarded result with replay evidence or a SMERC-blocked JSON-RPC error response.
- Added an MCP Proxy Runner that turns MCP-style tool-call governance into shadow/enforce proxy responses, forwarding decisions, Decision Lifecycle Ledger evidence, DLL Intelligence summaries, reports, documentation, and tests.
- Added Microsoft ecosystem and MCP runtime-governance positioning materials, including a bounded Microsoft Tech Community post draft that points reviewers to the working MCP tool governance adapter without claiming partnership, certification, or production readiness.
- Added MCP tool-call governance adapter, examples, docs, generated reports, and tests that map MCP-style tool-call metadata into SMERC recoverability decisions and SPARTa route behavior before execution.
- Added a one-command API smoke test that checks health, readiness, schema discovery, evaluation, runtime health, and operator status for local or hosted pilot APIs with explicit evidence boundaries.
- Added authenticated `/v1/operator/status` API support with SDK helpers and OpenAPI coverage so pilot operators can inspect runtime health, active policy identity, decision activity, and readiness caveats programmatically.
- Added runtime health gating to operator status reports so latency, SLO status, unavailable rate, and observed evaluation count are visible beside policy bundle, readiness, and decision activity.
- Added API-observed runtime latency capture on persisted decisions so `/v1/runtime/health-metrics` can calculate tenant-scoped p50/p95/p99 latency from stored evaluations instead of reporting unknown latency after live API use.
- Added runtime health metrics reporting and a tenant-scoped `/v1/runtime/health-metrics` API surface for decision volume, posture distribution, p50/p95/p99 latency when observations exist, unavailable evaluations, fail-closed behavior, and evidence-labeled observation boundaries.
- Added signed policy bundle manifests that bind SPL, runtime policy identity, artifact hashes, approval metadata, activation requirements, and verification results for pilot operator review without claiming OPA bundle parity.
- Added pilot operator status reporting and OPA-style decision log export so existing policy, audit, and platform teams can inspect active policy/profile versions, readiness, decision distribution, unavailable evaluations, reason codes, controls, and replay IDs without claiming OPA parity.
- Added a GitHub Actions customer pilot intake packet and validator for determining whether a prospect has a safe metadata boundary, owners, review process, success metrics, and 10 to 25 sample actions before week-zero qualification.
- Added a CISO 5-minute proof package that connects the product claim, credibility packet, GitHub Actions operator quickstart, readiness report, and 30-day observe-mode pilot ask.
- Added a GitHub Actions pilot operator quickstart and readiness generator that check whether the first observe-mode workflow has repository evidence, metadata boundaries, metrics, stop conditions, and day-30 go/no-go criteria before customer setup.
- Added bounded credibility-partner outreach language that points reviewers to the public credibility page and GitHub repo while avoiding production-readiness claims.
- Added a Credibility Partner Review Packet that converts the Governance Pattern Atlas into public links, a 30-minute review path, pilot-fit questions, and bounded outreach language.
- Added a Governance Pattern Atlas that consolidates AML, change management, security response, model risk, and SRE benchmark families into one credibility-partner evidence summary.
- Added an SRE/incident-management-inspired governance benchmark with reliability automation scenarios, CLI/report generation, documentation, and tests comparing incident playbooks with recoverability-aware runtime posture.
- Added a model-risk-inspired governance benchmark with AI-agent scenarios, CLI/report generation, documentation, and tests separating model approval status from recoverability-aware runtime action permission.
- Added a security-response-inspired governance benchmark with SOAR-style playbook scenarios, CLI/report generation, documentation, and tests comparing automated response playbooks with recoverability-aware runtime posture.
- Added a change-management-inspired governance benchmark with GitHub Actions scenarios, CLI/report generation, documentation, and tests comparing traditional change labels with recoverability-aware runtime posture.
- Added customer metadata validation to block unreplaced samples, unconfirmed substitution checklists, sample metrics, review-only prospects, and incomplete action intake before customer pilot package generation.
- Added customer metadata substitution guidance and checklist for safely replacing public samples with prospect-specific inputs before generating a core pilot package.
- Added a one-command core pilot package builder that outputs routing, action intake, handoff, and evidence summary artifacts into a review folder.
- Added pilot evidence summary generation that combines prospect routing, customer action intake, handoff status, and reviewer metrics into a go/no-go package.
- Added prospect routing to classify interested organizations into the core GitHub Actions pilot, SMERC-F financial shadow-mode pilot, or review-only path.
- Added SMERC-F stablecoin/blockchain pilot-fit guidance and a bounded financial shadow-mode pilot path while keeping GitHub Actions as the primary pilot wedge.
- Added an AML-inspired SMERC-F financial governance spur with scenarios, benchmark CLI, generated report, documentation, and tests comparing AML-style alerting with recoverability-aware action posture.
- Added a pilot handoff checklist and example to gate the transition from reviewer quickstart and customer action intake into observe-mode setup.
- Added metadata-only customer action intake for scoring prospect workflow examples before a shadow-mode pilot, including sample data, CLI, documentation, and tests.
- Added a one-command reviewer quickstart that generates PR Guardian, SPARTa, DLL, CISO seed, and benchmark artifacts into a single local proof package.
- Added accelerator-readiness and MACH37-readiness materials that keep SMERC focused on cyber review, GitHub Actions pilot proof, external-review signals, and evidence boundaries before future applications.
- Added YC next-cycle readiness materials that convert the missed Fall 2026 on-time deadline into an evidence-first application plan and bounded future application draft.
- Added `smerc.runtime-contract-index.v1`, a machine-readable assembly map for SMERC runtime contracts, handoffs, boundaries, schema, example, documentation, and tests.
- Added `smerc.sparta-vocabulary.v1`, a machine-readable SPARTa vocabulary for lifecycle verbs, route states, control verbs, evidence events, failure reasons, adapter interpretation, schema, example, documentation, and tests.
- Added local performance and latency reporting to the end-to-end PR Guardian proof loop, plus a competitive gaps and build-priorities note covering where OPA, AI gateways, access-control systems, approval workflows, and GRC platforms are stronger today.
- Added an end-to-end PR Guardian demo that connects an AI-assisted pull request request to a SMERC runtime decision, PR comment/certificate, SPARTa route, Decision Lifecycle Ledger, DLL Intelligence summary, generated reports, documentation, and tests.
- Added GitHub PR Guardian for AI-assisted pull requests, including PR comment rendering, hash-bound certificate artifacts, a workflow example, documentation, generated reports, and tests.
- Added DLL Intelligence for multi-ledger governance memory: near-miss detection, override effectiveness, rollback performance, recurring evidence gaps, drift signals, review-gated policy queue, schema, example portfolio, reports, documentation, and tests.
- Added a Model and Agent Fitness Layer that scores candidate executors by task fit, data boundary, tool authority, recoverability, reliability history, cost, and latency before selecting an execution posture.
- Added model and agent routing examples, documentation, CLI support, and tests.
- Added an AI-assisted build and red-team strategy that assigns roles to coding agents, second-opinion reviewers, GitHub-native agents, long-running agents, and human experts without treating AI output as validation.
- Added `smerc.beacon.v1`, a machine-readable public discovery manifest for agents, tools, reviewers, and search systems, with validation and overclaim checks.
- Added `smerc.agent_handshake.v1`, a reference protocol connecting beacon discovery, agent declaration, executor fitness, recoverability scoring, controls, and replay.
- Added authenticated `POST /v1/agent/handshake` runtime API support with tenant policy evaluation, scoped authorization, schema discovery, security-event logging, and API tests.
- Added Python and JavaScript SDK helpers for calling authenticated agent handshakes.
- Added a generic Agent Handshake integration runner that maps SMERC postures into safe agent-runner states without executing actions.
- Added an OpenAPI 3.1 pilot API contract with endpoint-coverage tests against the server discovery schema.
- Added a customer pilot operating kit covering kickoff, integration questionnaire, data boundary, weekly review, 30/60/90 plan, sample report, responsibilities, and go/no-go criteria.
- Added a design-partner qualification checklist that screens workflow fit, recoverability pain, metadata readiness, reviewer capacity, buyer ownership, data boundary, measurement readiness, and urgency before offering a pilot.
- Added a machine-readable design-partner fit scorer with example input, CLI JSON/Markdown output, blocker detection, offer recommendation, and tests.
- Added a first-pilot path that defines week-zero qualification, week-one observe setup, 30-day review, success metrics, evidence package, and commercial boundary.
- Added a first-pilot packet generator that combines the GitHub Actions pilot manifest with the design-partner fit screen to produce JSON/Markdown start-decision packets.
- Added a findability and AI-discovery guide covering canonical public links, search language, indexing assets, GitHub topics, and distribution checklist.
- Added acronym-expansion guidance for Structural Momentum Entropy Range Confidence on key discovery surfaces.
- Added a naming and search style guide using the brand/category/problem pattern for public labels.
- Added a public discovery audit CLI that checks local site exports for required search, AI-readable, beacon, sitemap, and naming metadata.
- Added generated public discovery audit JSON/Markdown reports and tests for the current public site metadata.
- Added a public review snapshot summarizing current maturity, working artifacts, recent improvements, first review path, pilot path, and remaining evidence gaps.
- Added v0.14 public-review release notes for external reviewers, validation, pilot discussion, and claim boundaries.
- Added a Human/AI Pilot Operating Model defining the split between AI-proposed actions, SMERC scoring, and human-owned validation, labels, accountability, and go/no-go decisions.
- Added a GitHub Actions pilot launch runbook and machine-readable pilot manifest covering local shadow mode, remote API mode, OIDC mode, evidence collection, and stop conditions.
- Added a GitHub Actions pilot artifact summarizer that converts downloaded `smerc-decision.json` reports into JSON/Markdown operating summaries without claiming customer outcome evidence.
- Added pricing and pilot-evidence positioning that ranges early paid pilots, centers the sale on measured pilot outcomes, and bounds the Decision Lifecycle Ledger as evidence support rather than a compliance guarantee.
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

