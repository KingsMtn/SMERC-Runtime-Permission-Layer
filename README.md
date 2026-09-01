# Pre-Execution Recoverability Control for AI Agents and MCP Tool Calls

[![Tests](https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/actions/workflows/tests.yml/badge.svg)](https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/actions/workflows/tests.yml)

## External Technical Review Edition

SMERC is a pre-execution recoverability control layer for AI agents, MCP tool calls, GitHub Actions, cloud automation, financial actions, and other high-impact workflows. The reference implementation is runtime permission infrastructure.

Mission: SMERC helps intelligent systems make safer decisions before irreversible actions occur, so people and organizations can trust the technology shaping their lives.

It sits between automated systems and consequential actions. Before an AI agent, workflow bot, MCP tool, or deployment process sends data, changes infrastructure, deploys code, modifies permissions, moves money, or calls a high-impact API, SMERC evaluates whether the action is recoverable enough to proceed.

Public reviewer site: https://admirable-sorbet-9986d5.netlify.app/

Category definition: https://admirable-sorbet-9986d5.netlify.app/pre-execution-recoverability-control.html

Glossary: https://admirable-sorbet-9986d5.netlify.app/glossary.html

Fast reviewer paths:

- CISO or security architect: `docs/CISO_Security_Architect_15_Minute_Review.md`
- Company reviewer front door: `docs/Company_Reviewer_Front_Door.md`
- Serious reviewer bundle: `docs/Serious_Reviewer_Bundle.md`
- AI/search reviewer: `docs/AI_Readable_Reviewer_Bundle.md`
- Technical reviewer: `docs/External_Review_Start_Here.md`
- Cloud infrastructure reviewer: `docs/Cloud_Admin_Proof_Pack.md`
- Complete lifecycle proof: `docs/Complete_Lifecycle_Proof.md`
- Skeptical competitive review: `docs/External_Signal_And_Competitive_Review.md`
- Market signal to proof map: `docs/Market_Signal_To_Proof_Map.md`
- Accelerator/adjacent company map: `docs/Accelerator_And_Adjacent_Company_Map.md`
- Public scenario benchmark: `docs/Public_Action_Governance_Benchmark.md`
- Pilot reviewer: `docs/Pilot_Intake_Template.md`
- Strategic/platform reviewer: `docs/Why_SMERC_Fits_Strategic_Platforms.md`

SMERC is short for Structural Momentum Entropy Range Confidence. It evaluates a proposed action before execution and returns a replayable posture:

- `ALLOW`
- `THROTTLE`
- `FREEZE`
- `DENY`
- `ESCALATE`

The first integration is a GitHub Actions gate for AI-assisted code, deployment, and infrastructure workflows. The same core contracts also support MCP-style tool-call governance and metadata-trust checks for agentic runtimes.

## Start Here: GitHub Actions Shadow-Mode Pilot

The primary pilot is intentionally narrow:

> Run SMERC in observe mode on one GitHub Actions workflow, score proposed automated actions before execution, preserve replayable evidence, and compare SMERC posture against existing reviewer judgment.

This is the clearest commercial path for a security, platform, or AI governance team because it does not require replacing IAM, OPA, branch protection, code review, CI/CD approvals, SIEM, or existing change-management controls.

Use this sequence:

1. Read `pilot_package/First_Pilot_Path.md` to confirm whether the workflow is a valid first pilot.
2. Read `docs/GitHub_Actions_Pilot_Operator_Quickstart.md` for the shortest install-and-measure path.
3. Run `python -m reference_engine.github_actions_pilot_readiness --pretty` to generate the readiness report.
4. Run SMERC in `observe` mode only.
5. Review posture distribution, reviewer agreement, false release candidates, false constraint candidates, useful constraint examples, unavailable evaluations, and latency impact before considering recommendation or enforcement.

Current status: pilot-ready for shadow-mode technical review. Not production-certified, compliance-attested, or customer-proven to reduce incidents.

## Competitive Reality Check

SMERC is not the only project working near agent runtime governance. OPA, AI gateways, sandboxed agent runtimes, MCP security tools, approval workflows, and signed audit systems already solve adjacent pieces of the problem.

The narrow SMERC wedge is pre-execution recoverability control:

> Existing systems ask whether an agent or workflow is authorized. SMERC asks whether the proposed action is recoverable, bounded, and evidenced enough to execute now, and preserves why that decision was made.

Read `docs/External_Signal_And_Competitive_Review.md` for the skeptical comparison, public signal review, overlap risks, and current non-claims.

Read `docs/Accelerator_And_Adjacent_Company_Map.md` for the accelerator and adjacent-company view. That document explains why SMERC should be positioned as a recoverability checkpoint that complements agent authorization, MCP infrastructure, AI gateways, sandboxes, approval workflows, and audit systems instead of pretending those categories do not exist.

## AI-Readable Reviewer Bundle

SMERC has a structured reviewer bundle for AI assistants, search systems, technical reviewers, and company evaluators:

- Human guide: `docs/AI_Readable_Reviewer_Bundle.md`
- Machine-readable bundle: `examples/ai_reviewer_bundle.json`
- Public site companion: `https://admirable-sorbet-9986d5.netlify.app/ai-review.json`

Work: stable summary, implemented surfaces, evidence links, non-claims, review sequence, and search terms.

Result: reviewers and AI systems can summarize SMERC without guessing from scattered pages.

Impact: the project becomes easier to inspect, compare, index, and route to the right reviewer while preserving the boundary that public indexing is not customer validation.

## Public Action Governance Benchmark

The public benchmark turns outside market patterns into a repeatable SMERC test set. It covers MCP tool calls, sandboxed coding agents, cloud administration, financial runtime actions, signed execution tickets, and security approval workflows.

Run:

```bash
python -m reference_engine.runtime_benchmark_suite examples/public_action_governance_benchmark.json \
  --json-output reports/public_action_governance_benchmark.json \
  --markdown-output reports/Public_Action_Governance_Benchmark.md \
  --pretty
```

Work: realistic metadata-only action scenarios.

Result: SMERC posture distribution and decision differences versus simple allow/deny.

Impact: reviewers can see whether recoverability creates useful middle states before a company shares private data or grants execution authority.

## Start Here: Self-Service Company Evaluation

If you are a company reviewer and want to test SMERC without a live integration, start with `docs/Company_Reviewer_Front_Door.md` or `customer_eval/README.md`.

That kit gives a 20-minute metadata-only path:

1. Choose one workflow family.
2. Replace `examples/customer_metadata_template.json` with 5 to 25 safe action records.
3. Run `python -m reference_engine.customer_evaluation`.
4. Review hard admission results, SMERC postures, SPARTa routes, Decision Lifecycle Ledger evidence, autonomy-budget impact, and pilot-fit output.
5. Move to a shadow-mode pilot only if reviewers find useful differences from existing controls.

Public page: https://admirable-sorbet-9986d5.netlify.app/customer-evaluation.html

This self-service path is designed to reduce founder explanation. It still requires customer-owned reviewer judgment before any pilot or enforcement discussion.

For the shortest complete reviewer package, run:

```bash
python -m reference_engine.serious_reviewer_bundle --workflow-family general --requested-actions 10 --pretty
```

This writes `reports/serious_reviewer_bundle/Serious_Reviewer_Bundle.md` plus the customer evaluation, postcondition evidence, performance, customer-owned metadata request, and external reviewer response assessment reports. See `docs/Serious_Reviewer_Bundle.md`.

Financial-services reviewers should use the Financial Runtime path, internally called SMERC-F:

```bash
python -m reference_engine.customer_evaluation examples/smerc_f_customer_eval_actions.json --pretty
```

SMERC-F covers metadata-only payment, refund, treasury, stablecoin, tokenized-collateral, wallet-policy, transaction-limit, and reserve-status actions. The public-data replay also adds a financial reason-code layer for low settlement reversibility, weak evidence, liquidity fragility, redemption pressure, collateral exposure, counterparty concentration, and automation velocity. The external financial signal adapter can consume AML/KYT-, wallet-screening-, fraud-, Travel Rule-, treasury-risk-, reserve-monitoring-, blockchain-analytics-, and smart-contract-risk-style outputs as evidence before recoverability scoring. It is not AML compliance, sanctions screening, fraud detection, custody, settlement, trading, payment execution, legal advice, or production financial-control certification.

## Start Here: Pilot Intake Report

If a reviewer wants the most practical first test, use `docs/Pilot_Intake_Template.md` and `examples/pilot_intake_template.json`.

That path asks for 5 to 25 metadata-only actions plus the company's current posture for each action: `ALLOW`, `BLOCK`, `REVIEW`, or `UNKNOWN`. SMERC then generates a comparison report showing where current controls and SMERC differ, whether any actions are constrained rather than blocked, which actions have the highest irreversible exposure, and whether a shadow-mode pilot is justified.

For a completed synthetic intake, use `examples/pilot_intake_filled_examples.json`.

Reviewers who prefer GitHub can open a structured pilot intake request:
`https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/issues/new?template=pilot_intake_request.md`.

Run:

```bash
python -m reference_engine.pilot_intake_report examples/pilot_intake_template.json \
  --json-output reports/pilot_intake/pilot_intake_report.json \
  --markdown-output reports/pilot_intake/Pilot_Intake_Report.md \
  --pretty
```

This is the best current handoff from public interest to a concrete company review. It is still metadata-only and does not prove production safety, compliance, customer demand, or enforce-mode readiness.

## Fastest Local Proof

Run one synthetic customer action through the current software path:

```bash
python -m reference_engine.customer_proof_loop examples/customer_proof_action.json --output-dir reports/customer_proof_loop --pretty
```

This produces a JSON evidence bundle and Markdown report showing:

- runtime admission gate result
- recoverability decision
- SPARTa route
- Recovery Authority Gate for paused or escalated continuation
- Decision Lifecycle Ledger chain
- pass/fail checks for hard gates, recoverability, route execution, and ledger validity

Read `docs/Customer_Proof_Loop.md` for the proof boundary and customer-use notes.

## Complete End-To-End Lifecycle Proof

Run one synthetic action through the assembled SMERC governance loop:

```bash
python -m reference_engine.complete_lifecycle_proof
```

Work: runtime admission, recoverability scoring, SPARTa routing, Recovery Authority Gate, action-bound permit verification, synthetic execution result, and Decision Lifecycle Ledger evidence.

Result: the reference case returns `COMPLETE`: `ADMIT -> FREEZE -> PAUSE -> UNLOCK -> THROTTLE -> CONSTRAINED_EXECUTE -> permit verified -> execution succeeded -> ledger valid`.

Impact: reviewers can see the product as one lifecycle. A risky action pauses before execution, cannot unlock itself, and can continue only after separate authority, fresh recovery evidence, bounded routing, permit gating, and replayable ledger evidence.

Read `docs/Complete_Lifecycle_Proof.md` and `reports/complete_lifecycle/Complete_Lifecycle_Proof_Report.md`.

## Pilot-In-A-Box

Run the multi-pack pilot preview when a reviewer wants to see SMERC operate across several workflow families before replacing examples with company-owned metadata:

```bash
python -m reference_engine.pilot_in_a_box --pretty
```

This writes `reports/pilot_in_a_box/Pilot_In_A_Box_Report.md` plus JSON evidence for general AI-agent actions, cloud-admin actions, financial-runtime actions, and one single-action proof loop. See `docs/Pilot_In_A_Box.md`.

Work: hard evidence gates, recoverability scoring, SPARTa routes, Decision Lifecycle Ledger evidence, autonomy impact, and pilot-fit signals.

Result: a company receives a concrete reviewer package instead of a slide-only explanation.

Impact: reviewers can decide whether a bounded shadow-mode pilot is worth time before sharing sensitive data or granting execution authority.

## Public Language

SMERC should lead with familiar category language, not internal layer names.

Preferred public phrase:

> Pre-execution recoverability control for AI agents, MCP tool calls, GitHub Actions, cloud automation, financial actions, and high-impact workflows.

Secondary technical category:

> Recoverability-aware runtime permission infrastructure.

Internal names come after the flow is understood: signal and evidence intake, recoverability decision, execution routing and controls, and decision lifecycle evidence. In the reference implementation those layers are called SPARK, SMERC, SPARTa, and DLL. See `docs/Public_Language_And_Naming.md`.

## What Exists Now

The current build includes:

- versioned SMERC Action Language and Decision Language contracts
- machine-readable runtime contract index showing how the decision engine, execution routing, permits, control evidence, DLL, and DLL Intelligence fit together
- evidence and unknowns registry with deployment-limiting falsification rules
- tenant-scoped policy calibration and evidence provenance admission
- agent identity gate that checks actor authority, tool-family permission, autonomy level, credential scope, and recent behavior before action execution
- signed, action-bound, single-use authorization permits
- signed, action-bound control-evidence receipts for configured execution adapters
- execution-routing layer that converts SMERC decisions into executable, constrained, paused, blocked, or review-required tool routes; internally this layer is called SPARTa
- machine-readable execution-routing vocabulary for lifecycle verbs, route states, control verbs, evidence events, and fail-closed adapter interpretation
- execution adapter registry and authenticated API route endpoint for stored SMERC decisions
- optional HMAC-signed route reports for pilot-grade tamper detection
- static adapter conformance report that checks declared adapter capabilities across ALLOW, THROTTLE, FREEZE, DENY, and ESCALATE route behavior
- GitHub deployment adapter route binding that verifies route replay, posture, executable state, and required controls before command execution
- MCP-style tool governance adapter that maps proposed agent tool calls into SMERC recoverability posture, route behavior, and client/proxy recommendations before execution
- MCP Tool Risk Scanner that lets reviewers triage MCP tool definitions before granting autonomous agents tool access
- MCP Proxy Runner that turns MCP-style tool-call governance into shadow/enforce proxy responses with optional agent identity admission and DLL evidence
- MCP Transport Proxy sample that wraps a JSON-RPC-style `tools/call` request and returns either a forwarded result or a SMERC-blocked proxy error, with an identity-required pilot-hardening option
- MCP Governance Gateway that evaluates registry-defined MCP tool-call sessions with loop pressure, scope pressure, session-budget metering, proxy actions, SPARTa routes, DLL evidence, and SMERC-F financial tool-family support
- deterministic ref-gate-style metadata checks for typed contract validity, attestation validity, least-privilege confirmation, and expected object shape before recoverability scoring is allowed to influence high-impact MCP tool calls
- Customer Evaluation runner that accepts 5 to 25 metadata-only customer actions and returns Ref-gate results, SMERC postures, SPARTa routes, DLL evidence, autonomy budget impact, and a pilot-fit recommendation
- Customer-Owned Metadata Request generator that gives external reviewers a safe ask for replacing public examples with 5 to 25 metadata-only actions from one real workflow
- External Reviewer Metadata Response assessor that classifies reviewer-supplied metadata as ready, limited, or not ready before customer-specific evaluation
- Financial Runtime Customer Evaluation pack, internally called SMERC-F, with finance-specific metadata-only actions for refunds, payment retries, treasury rebalancing, stablecoin liquidity, tokenized collateral, wallet-policy changes, transaction limits, and reserve-status publication
- SMERC-F External Financial Signal Adapter that normalizes AML/KYT-, wallet-screening-, fraud-, Travel Rule-, treasury-risk-, reserve-monitoring-, blockchain-analytics-, and smart-contract-risk-style outputs into recoverability scoring evidence without claiming to replace those systems
- Cloud Admin Customer Evaluation pack with metadata-only IAM, network, database, Kubernetes, DNS, rotation, capacity, and backup-policy actions for infrastructure review
- Cloud Admin Proof Pack that expands the cloud-admin sample into 24 scenarios with cloud-specific reason codes, Work / Result / Impact explanations, SPARTa route evidence, autonomy-budget impact, and DLL validity
- Cloud Metadata Connector that converts read-only IAM, Terraform, CloudTrail-style, Kubernetes, DNS, and backup-policy export summaries into strict SMERC customer-evaluation metadata without live cloud credentials
- Public Benchmark Ingestion Pack that maps representative public agent-governance, MCP-security, action-boundary, consequence, cloud, and financial benchmark shapes into SMERC customer-evaluation actions without claiming official benchmark scores
- Serious Report Performance harness that measures local p50, p95, and maximum latency for major proof paths without making production SLA claims
- repository-native Runtime Customer Evaluations GitHub Actions workflow that runs the general, cloud-admin, financial runtime, or company-template evaluation packs from the Actions tab and uploads review artifacts
- Self-Service Pilot Connector that turns mixed GitHub Actions/action-language and MCP transport examples into a compact pilot-fit decision package
- cloud automation guardrails positioning for infrastructure-as-code, IAM, Kubernetes, database, deployment, and destructive cloud-resource actions
- control mapping library that maps SMERC execution controls to declared native tool mechanisms and evidence requirements
- replayable governance report generator that assembles decision, route, control mapping, and lifecycle evidence into one review package
- Decision Lifecycle Ledger that chains request, evidence, evaluation, human interaction, execution, outcome, and reviewed learning recommendations
- end-to-end PR Guardian demo connecting SMERC decision, PR comment/certificate, execution route, Decision Lifecycle Ledger, and DLL Intelligence
- scoped workload principals with proposer, issuer, executor, reviewer, and auditor separation
- short-lived, scope-narrowed workload sessions issued from static pilot principals
- GitHub Actions OIDC verification with repository-, workflow-, ref-, environment-, and run-bound attribution
- recoverability-aware scoring engine
- model and agent fitness routing for selecting qualified executors
- machine-readable SMERC Beacon manifest for AI/tool discovery
- Agent Handshake Protocol connecting beacon discovery to executor routing and action posture evaluation
- signal and evidence intake path that validates non-secret evidence and compiles it into strict SMERC Action Language; internally this path is called SPARK
- Runtime Evidence Trust Gate that caps or rejects decisions when high-impact metadata comes only from the proposing agent instead of a trusted proxy, OIDC claim, adapter, audit event, ticket, or reviewer record
- Content Evidence Adapter that consumes trusted scanner, eval, policy, and reviewer signals for code, SQL, email, DLP, prompt-injection, malware, secrets, and other content-risk findings without replacing those systems
- Fallback Policy Layer that deterministically fails safe when scanners, policy bundles, metadata, adapters, review queues, rollback plans, or SMERC runtime dependencies are unavailable, stale, incomplete, conflicting, or timed out
- Constraint Eligibility Layer that preserves hard denies before recoverability can modify a runtime decision
- Timing Evidence reports for decision latency, route latency, workflow overhead, cancellation, rollback, and unavailable evaluations
- Postcondition Evidence report that compares SPARTa-required controls with observed control, execution, hold, and rollback evidence
- one-command Customer Proof Loop that runs runtime admission, recoverability scoring, SPARTa routing, and Decision Lifecycle Ledger evidence into one reviewable report
- complete lifecycle proof connecting runtime admission, recoverability scoring, SPARTa routing, Recovery Authority Gate, action-bound permit verification, synthetic execution result, and Decision Lifecycle Ledger evidence
- self-contained GitHub Actions pilot package generator that assembles signal intake, eligibility, SMERC decision, execution route, DLL, DLL Intelligence, and timing evidence
- scoring-invariant verification for recoverability and executor fitness math
- Self-Governance Sandbox that scores proposed SMERC policy, threshold, adapter, and scoring changes before they can affect SMERC itself
- Autonomy Health operating model for deciding whether an AI agent, workflow, or tool family should keep, reduce, suspend, or requalify its level of independence over time
- Autonomy Budgeting reference engine that meters current AI independence by action count, scope units, cumulative risk spend, ref-gate failures, and blocked or held attempts
- Earned Autonomy reference engine that converts historical review agreement, overrides, ref-gate history, rollback evidence, false releases, incidents, scope discipline, and evidence quality into a starting autonomy tier
- Autonomy Continuance reference engine that evaluates Authority Provenance, Intent Integrity, Consequence Horizon, Collective Autonomy, and Right To Continue after an actor has already begun operating
- Recovery Authority Gate that evaluates whether a paused, frozen, denied, or escalated action can be reopened through verified authority, fresh evidence, a bounded recovery path, action-bound permits, and ledger evidence
- Ref-gated runtime proof loop showing hard mechanical evidence gates before SMERC recoverability scoring, SPARTa routing, autonomy budget impact, and DLL evidence
- commercial-readiness language audit for checking public materials against evidence boundaries and unsupported claim risk
- authenticated, tenant-scoped REST API service
- OpenAPI 3.1 pilot API contract
- SQLite pilot audit store with idempotent decision replay
- immutable pilot review records and denominator-aware metrics
- dependency-free pilot review console
- GitHub PR Guardian that renders PR comments and hash-bound certificates for AI-assisted changes
- GitHub Actions gate
- generic Agent Handshake integration runner
- local and authenticated remote GitHub Action evaluation
- permit-consuming GitHub deployment adapter with native controls, cancellation, rollback, and non-secret execution reports
- copyable GitHub Actions customer-evaluation workflow that runs metadata-only customer actions and uploads a review artifact without requiring SMERC API credentials
- dependency-free Python SDK for API pilots and integration tests
- dependency-free JavaScript SDK for Node, agent runners, GitHub tooling, and browser pilot utilities
- synthetic shadow-mode scenario packs
- evidence/report generators
- Render deployment profile

## Why This Repository Exists

This public repository is the external technical review edition of SMERC. It contains the implementation and documentation needed for a security, platform, or product team to determine whether SMERC is worth testing in shadow mode.

It intentionally excludes private legal drafts, patent strategy, competition submissions, investor materials, outreach records, and internal commercial planning.

## Partners And Community Review

SMERC is open to design-partner, integration-partner, research-review, and open-source contribution paths.

- Read `COMMUNITY.md` for the overall engagement model.
- Read `docs/Partner_Program.md` for design-partner and integration-partner fit.
- Read `docs/Community_Outreach_Kit.md` for consistent public language.
- Use the GitHub issue templates to suggest pilots, integrations, scenarios, or research review.

The current project is ready for technical review and shadow-mode pilot discussion. It is not production-certified, compliance-attested, or proven to reduce incidents in live environments.

## Strategic Review

If you are evaluating SMERC as a potential platform feature, strategic partnership, acquisition target, or serious design-partner candidate, start here:

- `docs/Strategic_Acquisition_Positioning.md` explains the acquisition-relevant thesis and what evidence is still missing.
- `docs/Strategic_Buyer_Map.md` maps the platform categories where SMERC may matter.
- `docs/Why_SMERC_Fits_Strategic_Platforms.md` compares SMERC's runtime checkpoint to IAM, policy engines, AI gateways, approvals, and audit logs.
- `docs/IP_Asset_Map.md` maps the strongest technical mechanisms and weaker broad claims to avoid.
- `docs/Technical_Diligence_Index.md` gives a short inspection path through the implementation.
- `docs/Strategic_Reviewer_Brief.md` gives a one-page external review brief.
- `docs/Strategic_Outbound_Message.md` gives a bounded message for requesting serious review.

Generate the strategic reviewer evidence packet:

```bash
python -m reference_engine.strategic_reviewer_packet --pretty
```

The strategic path is evidence-first: prove that recoverability-aware runtime permissioning changes reviewer judgment in a useful way before claiming broad commercial value.

## If You Are New To SMERC

Start here before reading the code:

- `docs/External_Review_Start_Here.md` gives external reviewers the shortest safe path through the repository.
- `docs/AI_Readable_Reviewer_Bundle.md` gives AI assistants, search systems, and human reviewers a stable summary of what SMERC is, what exists, what can be tested, and what should not be claimed.
- `examples/ai_reviewer_bundle.json` gives machine readers a structured review bundle with canonical links, implemented surfaces, review sequence, search terms, and non-claims.
- `docs/Accelerator_And_Adjacent_Company_Map.md` gives accelerator and strategic reviewers a blunt map of adjacent company categories and SMERC's recoverability-specific lane.
- `docs/CISO_Security_Architect_15_Minute_Review.md` gives CISOs and security architects the fastest serious review path from product claim to MCP Gateway proof, GitHub Actions pilot path, replay evidence, and pilot decision.
- `docs/AI_Agent_Recoverability_Governance.md` explains the institutional control gap: why AI-agent governance should ask whether an action is recoverable, not only whether it is allowed.
- `docs/Reviewer_Quickstart.md` gives reviewers a one-command path that generates a local proof package linking PR Guardian, Ref-gated tool-call screening, SPARTa, DLL, CISO seed evidence, and benchmark comparison.
- `docs/Customer_Evaluation.md` gives prospective design partners a one-command metadata-only evaluation path for testing 5 to 25 of their own AI-agent or automation actions before a pilot discussion.
- `docs/Run_Customer_Evaluation_From_GitHub.md` gives non-local reviewers a click-by-click path for running the public customer-evaluation workflow from GitHub Actions and downloading the report artifact.
- `docs/Company_Test_Package.md` gives companies a practical first test: copy `examples/customer_metadata_template.json`, replace it with 5 to 25 metadata-only actions from one workflow, run the evaluation, and decide whether a 30-day shadow-mode pilot is justified.
- `docs/Customer_Owned_Metadata_Request.md` gives reviewers the clean external ask: replace public examples with 5 to 25 safe metadata-only actions from one workflow, then pair the result with performance and postcondition evidence.
- `docs/External_Reviewer_Metadata_Response.md` checks whether a reviewer response is usable, too limited, or unsafe before treating customer-owned metadata as pilot evidence.
- `docs/Cloud_Admin_Customer_Evaluation.md` gives cloud security, SRE, platform, and infrastructure reviewers a runnable metadata-only evaluation pack for IAM, network, database, Kubernetes, DNS, rotation, capacity, and backup-policy actions.
- `docs/Cloud_Admin_Proof_Pack.md` gives cloud, SRE, DevOps, CI/CD, and AI-agent platform reviewers a 24-scenario proof pack with cloud reason codes for IAM expansion, network widening, data-plane destructive action, DNS cutover, rollback uncertainty, evidence gaps, production blast radius, and autonomy scope pressure.
- `docs/Cloud_Metadata_Connector.md` shows how read-only cloud-change exports can be normalized into SMERC customer-evaluation actions before any live AWS, Azure, Google Cloud, Cloudflare, Kubernetes, Terraform, DNS, database, or secrets-manager integration.
- `docs/Public_Benchmark_Ingestion.md` shows how public agent-governance, MCP-security, action-boundary, consequence, cloud, and financial benchmark shapes can be translated into SMERC runtime-evaluation metadata without claiming official upstream benchmark scores.
- `docs/Postcondition_Evidence.md` shows how to verify whether SPARTa-required controls actually happened after a route decision.
- `docs/Serious_Report_Performance.md` shows how to measure local p50, p95, and maximum latency for serious proof paths while preserving the boundary that local report timing is not production SLA evidence.
- `docs/Governance_Pattern_Atlas.md` explains the consolidated operating-model evidence showing SMERC as one runtime permission system across AML, change management, security response, model risk, and SRE.
- `docs/Credibility_Partner_Review_Packet.md` gives external reviewers a 30-minute packet for deciding whether metadata-only shadow-mode testing is worth discussing.
- `docs/Credibility_Partner_Outreach.md` gives a short, bounded outreach message for asking credibility partners to review SMERC without overclaiming readiness.
- `docs/ILION_Bench_Replay.md` explains how to replay the public ILION-Bench v2 agent execution-safety dataset through SMERC without committing the external dataset into this repository.
- `docs/Customer_Action_Intake.md` gives prospects a metadata-only action intake path for scoring their own workflow examples before a shadow-mode pilot.
- `docs/Pilot_Intake_Template.md` gives prospects the most practical first test: compare current `ALLOW`, `BLOCK`, `REVIEW`, or `UNKNOWN` outcomes against SMERC posture and generate a pilot intake report.
- `docs/Prospect_Routing.md` routes interested organizations to the core GitHub Actions pilot, financial runtime pilot, or review-only path.
- `docs/Core_Pilot_Package.md` builds the core pilot review folder in one command from routing, action intake, handoff, and evidence summary inputs.
- `docs/Runtime_Contract_Index.md` explains the machine-readable `smerc.runtime-contract-index.v1` assembly map for SMERC's contracts and handoffs.
- `docs/SPARK_Signal_Intake_And_Timing_Evidence.md` explains the proposed SPARK signal-intake layer and timing evidence metrics around recoverability decisions.
- `docs/Runtime_Admission_Gate.md` explains the reusable pre-scoring admission contract for identity, scope, permits, typed contracts, attestation, least privilege, object shape, and required evidence.
- `docs/Customer_Proof_Loop.md` gives reviewers a one-command path that runs a synthetic customer action through runtime admission, recoverability scoring, SPARTa routing, and Decision Lifecycle Ledger evidence.
- `docs/Runtime_Evidence_Trust_Gate.md` explains how SMERC screens whether action metadata is trustworthy enough to support a runtime decision.
- `docs/Content_Evidence_Adapter.md` explains how SMERC consumes trusted content-risk signals from scanners, eval platforms, policy engines, and reviewers without pretending to replace them.
- `docs/Fallback_Policy_Layer.md` explains deterministic fail-safe posture handling when evidence, scanners, adapters, policies, review queues, rollback plans, or runtime dependencies are unavailable or stale.
- `docs/Constraint_Eligibility_Layer.md` explains why recoverability is a permission modifier, not a substitute for authority, hard policy, or categorical denies.
- `docs/OpenSSF_Feedback_Alignment.md` explains how external OpenSSF issue #50 feedback sharpened the runtime order: hard mechanical evidence gates first, recoverability scoring second, route and audit evidence third.
- `docs/Policy_Bundle_Manifest.md` explains signed, versioned policy bundle manifests for reviewed SPL, profile, control, approval, and activation evidence.
- `docs/Operator_Status_And_OPA_Log_Export.md` explains the pilot operator status report, `/v1/operator/status` API, and OPA-style decision log export for existing policy/audit pipelines.
- `docs/Runtime_Health_Metrics.md` explains runtime health, latency, unavailable-evaluation, and fail-closed metrics for pilot operations.
- `docs/API_Smoke_Test.md` gives operators a one-command way to verify a local or hosted SMERC API path from health to evaluation to operator status.
- `docs/Public_Review_Snapshot.md` gives a compact current-status snapshot for reviewers who need the fastest honest orientation.
- `docs/Release_Notes_v0_14_Public_Review.md` gives a compact release-style summary for public review, validation, and pilot discussion.
- `docs/Plain_English_Product_Overview.md` explains what SMERC does, what exists now, and what is not proven yet.
- `docs/Public_Language_And_Naming.md` explains how public surfaces should lead with pre-execution recoverability control before internal layer names such as SPARK, SPARTa, and DLL.
- `docs/Category_Positioning.md` defines the sharper category position: SMERC is a pre-execution recoverability control layer, implemented as runtime permission infrastructure.
- `docs/CISO_5_Minute_Proof_Package.md` gives security executives the fastest proof path from claim to pilot ask without production-readiness claims.
- `docs/GitHub_PR_Guardian.md` explains the developer-facing PR review surface for AI-assisted code and deployment changes.
- `docs/End_To_End_PR_Guardian_Demo.md` shows the current modules working as one synthetic review loop from AI-assisted pull request to DLL Intelligence.
- `docs/Competitive_Gaps_And_Build_Priorities.md` states what adjacent products do better today and what SMERC should build next.
- `docs/Competitive_Proof_Data_Map.md` maps the proof categories used by adjacent MCP gateway, AI gateway, policy, and runtime governance products to SMERC-compatible public evidence.
- `docs/Competitive_Proof_Parity_Harness.md` explains the one-command report that runs SMERC across those same proof categories.
- `docs/Market_Signal_To_Proof_Map.md` connects public pain language, available benchmark/data shapes, current SMERC proof, and the next evidence work without treating public signal as customer validation.
- `examples/runtime_contract_index.json` gives agents, adapters, SDKs, and reviewers the canonical contract handoff map.
- `docs/Maturity_Model.md` defines the evidence-based maturity scale used for SMERC claims.
- `docs/CISO_30_Minute_Review_Package.md` gives CISOs a timed review path for deciding whether a shadow-mode pilot is justified.
- `docs/Thirty_Minute_Workflow_Proof.md` gives reviewers the shortest concrete path for testing one workflow and comparing SMERC with simple allow/deny review.
- `docs/CISO_Evidence_Walkthrough.md` gives reviewers a local end-to-end flow from seeded decisions to pilot console evidence packages.
- `docs/GitHub_Actions_Pilot_Operator_Quickstart.md` gives customer operators the shortest install-and-measure path for one observe-mode GitHub Actions workflow.
- `docs/GitHub_Actions_Pilot_Installer.md` gives reviewers a one-command package generator for the connected GitHub Actions pilot artifact folder.
- `integrations/github_actions/pilot_package_workflow.yml` gives reviewers a copyable GitHub Actions workflow that generates and uploads the complete pilot package without a remote API.
- `integrations/github_actions/customer_evaluation_workflow.yml` gives reviewers a copyable GitHub Actions workflow that runs the metadata-only customer evaluation package and uploads the report artifact without a remote API.
- `.github/workflows/customer-evaluations.yml` lets reviewers run the general and financial runtime customer-evaluation examples directly from this repository's GitHub Actions tab.
- `docs/CISO_GitHub_Inspection_Guide.md` shows what a security or platform reviewer should inspect first.
- `docs/Founder_Explanation_Card.md` gives a short nontechnical explanation for founder calls, YC-style applications, and design-partner conversations.
- `docs/Accelerator_Readiness_Track.md` defines when SMERC should move from technical review to accelerator applications or investor-facing submissions.
- `docs/MACH37_Application_Readiness.md` gives a cybersecurity-accelerator readiness frame for a future MACH37-style application.
- `docs/YC_Next_Cycle_Readiness_Plan.md` defines the evidence-first plan for making a later YC application stronger after missing the Fall 2026 on-time deadline.
- `docs/YC_Application_Evidence_Draft.md` gives YC-style language with explicit evidence slots that should not be filled until real customer or reviewer proof exists.
- `docs/Developer_Quickstart.md` gives technical reviewers a short run-and-inspect path.
- `schemas/smerc-runtime-api-openapi-v1.json` gives integration partners a reviewable OpenAPI 3.1 contract for the pilot API.
- `docs/Engine_Profile_And_Trace.md` explains domain profiles, score contributions, threshold trace, and transition guidance.
- `docs/Model_Agent_Fitness_Layer.md` explains how SMERC selects the qualified model, agent, or automation executor for a specific task.
- `docs/SMERC_Beacon.md` explains the machine-readable beacon that helps agents, tools, and reviewers discover SMERC governance boundaries.
- `docs/Agent_Handshake_Protocol.md` explains how an agent discovers SMERC, declares itself, proposes an action, receives a posture, and preserves a replay record.
- `docs/MCP_Tool_Governance.md` explains how SMERC can score MCP-style tool calls before execution and map them through SPARTa without replacing MCP, OAuth, IAM, or prompt defenses.
- `docs/MCP_Tool_Risk_Scanner.md` explains how to scan MCP tool definitions for recoverability and autonomy risk before those tools are granted to agents.
- `docs/MCP_Proxy_Runner.md` explains the local MCP proxy runner that returns shadow/enforce proxy actions and records Decision Lifecycle Ledger evidence.
- `docs/MCP_Transport_Proxy.md` explains the local JSON-RPC-style transport proxy sample for `tools/call` forwarding or blocking.
- `docs/MCP_Governance_Gateway.md` explains the registry-driven MCP gateway that evaluates tool-call sessions, repeated-call pressure, scope pressure, session-budget metering, SMERC posture, SPARTa route behavior, and SMERC-F financial tool profiles.
- `docs/SMERC_And_The_Ref_Pattern.md` explains how deterministic pre-execution checks for typed contracts, attestation, least privilege, and object shape prevent malformed or untrusted MCP tool calls from being scored around.
- `docs/Ref_Gated_Runtime_Proof_Loop.md` gives the executable proof loop for hard Ref gates before SMERC scoring, SPARTa routing, autonomy budget, and DLL evidence.
- `docs/Autonomy_Health_Framework.md` explains the continuous governance layer for deciding how much independence an AI agent, workflow, or tool family should retain over time.
- `docs/Autonomy_Budgeting_Framework.md` explains how SMERC meters current agent freedom by action budget, scope budget, risk spend, valid time window, and allowed tool tiers.
- `docs/Earned_Autonomy_Framework.md` explains how historical evidence sets the starting autonomy tier before the current session spends or loses that budget.
- `docs/Autonomy_Continuance_Framework.md` explains how Authority Provenance, Intent Integrity, Consequence Horizon, Collective Autonomy, and Right To Continue determine whether an AI actor can keep operating from its current point.
- `docs/Recovery_Authority_Gate.md` explains the governed unlock path after a SMERC pause: who or what can reopen the action, what evidence is required, and why the original proposing actor should not approve itself.
- `docs/Self_Service_Pilot_Connector.md` explains how a reviewer can run a mixed metadata-only sample bundle and receive a compact pilot-fit decision package.
- `docs/Cloud_Automation_Guardrails.md` explains how SMERC can be evaluated as a recoverability-aware checkpoint for cloud automation and infrastructure actions.
- `docs/MCP_Runtime_Governance_Positioning.md` explains SMERC's focused category position as recoverability-aware runtime governance for MCP-style tool calls and agent actions.
- `docs/Microsoft_Ecosystem_Positioning.md` gives Microsoft-oriented reviewers a bounded explanation of where SMERC can complement MCP, GitHub Actions, DevOps, identity, policy, and security operations.
- `docs/Microsoft_Tech_Community_Post_Draft.md` gives a careful public discussion draft for Microsoft ecosystem feedback without implying partnership, certification, or production readiness.
- `docs/AI_Assisted_Build_And_Red_Team_Strategy.md` explains how outside AI tools can help with engineering critique and agent simulation without replacing human validation.
- `docs/Scoring_Invariants_And_Calibration.md` explains the declared scoring invariants, what passes today, and what still requires design-partner calibration.
- `docs/Self_Governance_Sandbox.md` explains how proposed changes to SMERC itself are capped to test-only, reviewed, benchmarked, and recorded before activation.
- `docs/SPARTa_Router_Operations.md` explains how SMERC postures become execution routes for declared tool plans.
- `docs/SPARTa_v2_Execution_Adapter_Framework.md` explains how SPARTa can mature into the execution-adapter layer for GitHub Actions, ticketing, review, cloud, and financial workflows.
- `specification/SMERC_SPARTa_Vocabulary_v1.md` defines the machine-readable `smerc.sparta-vocabulary.v1` terms that agents and adapters should use instead of inventing route meanings.
- `docs/SPARTa_Adapter_Conformance.md` explains how the static adapter conformance harness checks declared SPARTa capabilities before pilot use.
- `docs/GitHub_Deployment_Adapter_Operations.md` explains how a supplied SPARTa route artifact can be bound to a one-time permit before GitHub deployment execution.
- `docs/Control_Mapping_Library.md` explains how abstract SMERC controls map to native mechanisms and evidence requirements for a tool path.
- `docs/Governance_Report_Generator.md` explains how to assemble decision, route, control mapping, and DLL artifacts into one replayable review report.
- `docs/Decision_Lifecycle_Ledger.md` explains how SMERC records the full governed life of a decision.
- `docs/Fake_Customer_Production_Like_Test.md` explains the AcmeCloud simulated customer environment that exercises safe, constrained, blocked, review-required, and rollback paths.
- `docs/Real_Public_Incident_Replay.md` explains how public incident reports are replayed through SMERC with analyst-assigned signal boundaries.
- `docs/SMERC_F_Profile_Packet.md` explains the SMERC-F financial-action profile packet and its commercial limits.
- `docs/SMERC_F_AML_Inspired_Spur.md` explains SMERC-F as an AML-inspired financial-action governance profile without claiming AML compliance or replacing financial-crime systems.
- `docs/Change_Management_Inspired_Governance.md` explains how SMERC complements change-management discipline by scoring runtime recoverability before GitHub Actions and production automation execute.
- `docs/Security_Response_Inspired_Governance.md` explains how SMERC complements SOAR and incident-response playbooks by scoring recoverability before security automation executes.
- `docs/Model_Risk_Inspired_Governance.md` explains how SMERC complements model-risk programs by separating model approval from runtime action permission.
- `docs/SRE_Incident_Inspired_Governance.md` explains how SMERC complements reliability automation by scoring whether incident mitigations are recoverable enough to execute.
- `docs/SMERC_F_Stablecoin_Blockchain_Pilot_Fit.md` explains when stablecoin, blockchain, payment, treasury, or tokenized-finance teams are a strong SMERC-F fit.
- `docs/SMERC_F_Fortune_500_Financial_Services_Review.md` gives Fortune 500 financial-services reviewers a safe metadata-only evaluation path for automated financial actions.
- `docs/SMERC_F_Metadata_Intake_Contract.md` defines the first safe SMERC-F customer intake boundary: metadata-only, shadow-mode, one workflow family, no live fund movement, and no production enforcement.
- `docs/SMERC_F_Financial_Source_Ingestion.md` explains how exported financial, stablecoin, blockchain, and incident metadata can be normalized into SMERC-F replay inputs.
- `docs/SMERC_F_External_Financial_Signals.md` explains how SMERC-F consumes external financial-risk signals as evidence while leaving AML/KYT, wallet screening, fraud, Travel Rule, treasury risk, reserve monitoring, blockchain analytics, and smart-contract risk systems as the source systems.
- `docs/SMERC_F_Regulatory_Context_Profile.md` explains how legislation-inspired operational context can inform SMERC-F scoring without making legal or compliance claims.
- `docs/SMERC_F_Financial_Public_Data_Replay.md` explains how public-data-shaped stablecoin, blockchain, and incident records are converted into SMERC-F replay scenarios.
- `docs/SMERC_F_Financial_Reason_Codes.md` explains the financial reason-code layer that turns public-data replay results into reviewer-readable work, result, and impact evidence.
- `docs/SMERC_F_Pilot_Evidence_Packet.md` explains how source-ingestion, regulatory-context, and replay reports combine into a single financial-services pilot review packet.
- `docs/SMERC_F_Customer_Evaluation.md` gives financial-services reviewers a metadata-only customer-evaluation path using the general customer-evaluation runner and finance-specific sample actions.
- `pilot_package/SMERC_F_Financial_Shadow_Mode_Pilot_Path.md` gives a bounded metadata-only SMERC-F pilot path for financial-action review without live fund movement.
- `pilot_package/Fortune_500_Financial_Services_Review_Checklist.md` screens whether a large financial-services review has the owners, data boundary, and metrics needed before a pilot is offered.
- `docs/Public_Review_And_Feedback.md` gives public reviewers and community posts a safe critique path.
- `docs/Community_Submission_Kit.md` gives careful, non-exaggerated public post drafts for Microsoft Tech Community, GitHub Community, LinkedIn, Hacker News, and Product Hunt.
- `docs/Public_Indexing_Assets.md` records the public status page, sitemap, robots file, `llms.txt`, and `humans.txt`.
- `docs/Findability_And_AI_Discovery.md` records the search and AI-discovery language needed for humans and tools to find SMERC accurately.
- `docs/Naming_And_Search_Style_Guide.md` defines the brand/category/search wording pattern for public pages and repository materials.
- `examples/domain_profiles/github_actions_strict.json` shows how a design partner can load a strict custom calibration profile without editing engine code.
- `docs/Python_SDK_Quickstart.md` shows how to call the SMERC API from Python without third-party dependencies.
- `docs/JavaScript_SDK_Quickstart.md` shows how to call the SMERC API from Node or browser-compatible JavaScript.
- `integrations/agent_handshake/README.md` shows how an agent runner should call the handshake API and map postures into safe execution states.
- `integrations/human_review/README.md` shows how SPARTa can package a review-required route into signed human-review request and response evidence before a live Slack, Teams, Jira, or ServiceNow adapter exists.
- `docs/Pilot_Evaluation_Checklist.md` and `examples/pilot_evaluation_checklist.json` give design partners a concrete evaluation checklist.
- `pilot_package/Pilot_Kickoff_Packet.md` and the adjacent pilot operating templates define how a customer pilot starts, runs, reviews, and reaches go/no-go decisions.
- `pilot_package/Design_Partner_Qualification_Checklist.md` helps screen whether a prospect is weak, exploratory, moderate, or strong fit before offering a pilot.
- `pilot_package/Human_AI_Pilot_Operating_Model.md` defines the split between AI-generated actions, SMERC scoring, and human-owned review, labels, and go/no-go decisions.
- `pilot_package/GitHub_Actions_Pilot_Launch_Runbook.md` and `examples/github_actions_pilot_manifest.json` give a concrete first-workflow launch path for a GitHub Actions shadow-mode pilot.
- `reference_engine.github_actions_pilot_readiness` generates a readiness report that checks whether the pilot manifest and repository evidence are ready for week-zero qualification and observe-mode setup.
- `pilot_package/GitHub_Actions_Customer_Pilot_Intake.md` gives interested prospects a metadata-only intake packet for determining whether one GitHub Actions workflow is ready for review-call and week-zero pilot qualification.
- `pilot_package/First_Pilot_Path.md` gives the shortest path from interested prospect to 30-day shadow-mode evidence.
- `pilot_package/Customer_Metadata_Substitution_Guide.md` explains how a prospect replaces public samples with metadata-only customer inputs safely.
- `docs/Customer_Metadata_Validation.md` checks whether prospect-specific inputs are ready before generating a customer pilot package.
- `pilot_package/Pilot_Handoff_Checklist.md` defines the required customer, reviewer, data-boundary, stop-condition, and success-metric gate before observe mode starts.
- `docs/Pilot_Evidence_Summary.md` generates the executive go/no-go wrapper from prospect route, customer action intake, handoff status, and reviewer metrics.
- `pilot_package/Pricing_And_Pilot_Evidence_Position.md` explains early pilot pricing and why the Decision Lifecycle Ledger should be positioned as evidence support, not a standalone compliance guarantee.
- `pilot_package/Level_5_Shadow_Mode_Pilot_Packet.md` gives a bounded design-partner pilot path and stop conditions.
- `reports/Pilot_Level_5_Readiness_Assessment.md` shows the generated readiness assessment and unresolved gaps.
- `specification/SMERC_SPL_v0.md` introduces a starter policy-language profile that compiles to the strict runtime policy contract.
- `reports/Proxy_Incident_Replay_Benchmark.md` shows proxy incident-replay evidence comparing simple allow/deny policy with SMERC recoverability-weighted posture decisions.
- `reports/Runtime_Governance_Benchmark.md` shows an expanded deterministic benchmark comparing SMERC postures against a simple allow/deny baseline across 132 scenarios, including public-pattern synthetic examples for developer-agent runtime controls, MCP argument risk, data exfiltration pressure, approval-memory reuse, replay regression, agent identity gaps, and autonomy-budget pressure.
- `reports/Governance_Pattern_Atlas.md` summarizes five governance-pattern benchmarks, 40 scenarios, and the unified evidence boundary for credibility-partner review.
- `reports/Credibility_Partner_Review_Packet.md` packages the public links, atlas summary, review questions, pilot-fit questions, and evidence boundaries for external credibility review.
- `reports/Runtime_Benchmark_DLL_Bundle.md` converts those benchmark decisions into hash-chained decision-time ledgers without fabricating live execution or outcome evidence.
- `reports/Change_Management_Governance_Benchmark.md` compares traditional change labels with SMERC runtime postures across GitHub Actions and production-change scenarios.
- `reports/Security_Response_Governance_Benchmark.md` compares security playbook outcomes with SMERC runtime postures across security automation scenarios.
- `reports/Model_Risk_Governance_Benchmark.md` compares model-governance outcomes with SMERC runtime postures across AI-agent action scenarios.
- `reports/SRE_Incident_Governance_Benchmark.md` compares SRE incident playbook outcomes with SMERC runtime postures across reliability automation scenarios.
- `reports/Pilot_Ledger_Intake_Result.md` shows how pilot-supplied reviewer, execution, outcome, and learning evidence can be appended to a DLL with ordering checks.
- `reports/Pilot_Ledger_Metrics_Report.md` summarizes completed DLL evidence with explicit denominators and sample-size caveats.
- `docs/Pilot_DLL_API.md` describes stateless API endpoints for submitting pilot DLL intake evidence and calculating DLL metrics.
- `docs/Decision_Certificate.md` describes digest-bound pilot certificates that summarize verified DLL records for replayable review.
- `reports/Decision_Certificate_Example.md` shows an example signed pilot certificate generated from a verified Decision Lifecycle Ledger.
- `reports/Decision_Lifecycle_Ledger_Example.md` shows a full pilot-grade lifecycle record from request through learning recommendation.
- `reports/End_To_End_PR_Guardian_Demo.md` shows the integrated PR Guardian proof path: runtime decision, PR artifact, SPARTa route, DLL record, and DLL Intelligence summary.
- `reports/SMERC_F_Profile_Packet.md` shows a financial-action profile packet across conservative, balanced, and permissive policies.
- `reports/Public_Discovery_Audit.md` shows the latest local audit of the public site's discovery metadata and AI-readable files.
- `reports/Commercial_Readiness_Language_Audit.md` shows the latest audit of public-facing repository language for positioning clarity, evidence boundaries, and unsupported claim risk.
- `COMMUNITY.md`, `CONTRIBUTING.md`, `docs/Partner_Program.md`, and `docs/Community_Outreach_Kit.md` describe how design partners, integration partners, researchers, and open-source contributors can engage.

The shortest accurate explanation is:

> SMERC helps companies decide whether AI-agent and automation actions are recoverable enough to execute now.

## Review In 10 Minutes

1. Read `docs/Plain_English_Product_Overview.md`.
2. Read `docs/CISO_30_Minute_Review_Package.md`.
3. Read `docs/Thirty_Minute_Workflow_Proof.md`.
4. Run `docs/CISO_Evidence_Walkthrough.md`.
5. Read `docs/CISO_GitHub_Inspection_Guide.md`.
6. Read `docs/Developer_Quickstart.md`.
7. Read `docs/Pilot_Evaluation_Checklist.md`.
8. Read `docs/Maturity_Model.md`.
9. Read `reports/Pilot_Level_5_Readiness_Assessment.md`.
10. Read `docs/CISO_Quick_Review.md`.
11. Read `docs/Security_Model.md`.
12. Inspect `reference_engine/recoverability_engine.py`.
13. Read `docs/Engine_Profile_And_Trace.md`.
14. Inspect `reference_engine/model_fitness.py` and read `docs/Model_Agent_Fitness_Layer.md`.
15. Inspect `reference_engine/beacon.py` and read `docs/SMERC_Beacon.md`.
16. Inspect `reference_engine/agent_handshake.py` and read `docs/Agent_Handshake_Protocol.md`.
17. Read `docs/AI_Assisted_Build_And_Red_Team_Strategy.md`.
18. Inspect `reference_engine/scoring_invariants.py` and read `docs/Scoring_Invariants_And_Calibration.md`.
19. Inspect `reference_engine/action_language.py` and `specification/SMERC_Action_Language_v1.md`.
20. Read `docs/Policy_Calibration_And_Evidence_Provenance.md`.
21. Inspect `api_server.py` and `reference_engine/audit_store.py`.
22. Review `integrations/agent_handshake/README.md`.
23. Review `integrations/github_actions/README.md`.
24. Read `docs/Pilot_Review_Metrics.md`.
25. Inspect `pilot_console/README.md`.
26. Inspect `reference_engine/authorization_permit.py` and `specification/SMERC_Action_Bound_Permit_v1.md`.
27. Read `docs/Scoped_Workload_Identity.md`.
28. Inspect `reference_engine/control_evidence.py` and `specification/SMERC_Control_Evidence_v1.md`.
29. Read `docs/Short_Lived_Access_Operations.md` and `specification/SMERC_Access_Token_v2.md`.
30. Read `docs/GitHub_OIDC_Operations.md` and `specification/SMERC_GitHub_OIDC_Trust_v1.md`.
31. Inspect `integrations/github_deployment/` and read `docs/GitHub_Deployment_Adapter_Operations.md`.
32. Inspect `reference_engine/sparta_router.py` and read `docs/SPARTa_Router_Operations.md`.
33. Read `docs/SPARTa_v2_Execution_Adapter_Framework.md`.
34. Inspect `integrations/human_review/README.md`.
35. Inspect `reference_engine/control_mapping.py` and read `docs/Control_Mapping_Library.md`.
36. Inspect `reference_engine/governance_report.py` and read `docs/Governance_Report_Generator.md`.
37. Inspect `reference_engine/decision_lifecycle_ledger.py` and read `docs/Decision_Lifecycle_Ledger.md`.
38. Read `docs/Python_SDK_Quickstart.md`.
39. Read `docs/JavaScript_SDK_Quickstart.md`.
40. Review `reports/Proxy_Incident_Replay_Benchmark.md`.
41. Review `reports/Scoring_Invariants_Report.md`.
42. Review `reports/Control_Mapping_Library_Example.md`.
43. Review `reports/Governance_Report_Example.md`.
44. Review `reports/Decision_Lifecycle_Ledger_Example.md`.
45. Review `reports/Commercial_Readiness_Language_Audit.md`.
45. Read `COMMUNITY.md` and `docs/Partner_Program.md` if you are evaluating partnership or pilot fit.
46. Run the Python and console tests.
47. Review `pilot_package/Level_5_Shadow_Mode_Pilot_Packet.md`.
48. Review `pilot_package/GitHub_Actions_Pilot_Launch_Runbook.md`.
49. Review `pilot_package/Human_AI_Pilot_Operating_Model.md`.

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
- domain profile, score contribution trace, and posture-threshold trace
- transition guidance showing what evidence or controls would move a decision toward a less restrictive posture
- policy identity, revision, mode, evidence ceiling, and hash
- replay ID and replay record
- an optional short-lived permit for eligible enforcement decisions
- authenticated principal identity bound into decisions, replays, reviews, and security events
- signed control-evidence attribution when configured at permit consumption
- a SPARTa route report when a posture must be converted into an executable tool plan
- a control mapping report showing whether required controls map to native tool mechanisms and evidence requirements
- a governance report that cross-checks decision, route, control mapping, and lifecycle artifacts
- an optional Decision Lifecycle Ledger record for request, evidence, evaluation, review, execution, outcome, and learning recommendation

## Model and Agent Fitness

`reference_engine/model_fitness.py` evaluates which model, agent, or automation executor is qualified for a proposed task. It is not a generic model leaderboard. It scores executor fit against required capabilities, data sensitivity, tool authority, recoverability, reliability history, cost, latency, impact scope, and anomaly pressure.

The output includes a recommended executor, allowed and blocked executors, execution posture, candidate rankings, model fitness score, risk-adjusted executor score, controls, reason codes, and a replay record.

```bash
python -m reference_engine.model_fitness examples/model_agent_routing_examples.json --pretty
python -m unittest tests.test_model_fitness -v
```

## Agent Identity Gate

`reference_engine/agent_identity.py` evaluates whether the requesting actor is allowed to ask for a tool action before recoverability scoring and SPARTa routing are trusted. It checks trust tier, authorized tool family, maximum autonomy level, credential scope, recent denials, recent overrides, and recent success rate.

The output includes `PASS`, `WATCH`, or `FAIL`, identity score, trust modifier, reason codes, recommended controls, and a plain-English summary. When customer evaluation includes agent identities, failed identity admission caps the action to `FREEZE` unless a stricter Ref-gate failure caps it to `DENY`.

```bash
python -m reference_engine.agent_identity examples/agent_identity_catalog.json \
  --actor release_agent \
  --tool github_actions.production_deploy \
  --autonomy execute \
  --side-effect external \
  --pretty
python -m unittest tests.test_agent_identity -v
```

See `docs/Agent_Identity_Gate.md`.

## SMERC Beacon

`examples/smerc_beacon.json` is a machine-readable discovery manifest for AI agents, automation tools, reviewers, and search systems. It points to canonical SMERC resources, declares governance surfaces, lists discovery endpoints, describes Model and Agent Fitness inputs and outputs, and preserves non-claims so tools do not overstate the project.

```bash
python -m reference_engine.beacon examples/smerc_beacon.json --pretty
python -m unittest tests.test_beacon -v
```

## Agent Handshake Protocol

`reference_engine/agent_handshake.py` connects SMERC Beacon discovery, agent declaration, Model/Agent Fitness routing, recoverability scoring, and replay into a single handshake response.

```bash
python -m reference_engine.agent_handshake examples/agent_handshake_request.json --pretty
python -m unittest tests.test_agent_handshake -v
```

The same protocol is available through the authenticated runtime service at `POST /v1/agent/handshake` with `actions.evaluate` scope. The endpoint returns the combined handshake posture and replay record, then records an `agent.handshake.evaluated` security event for review.

The reference handshake is pilot-grade. It does not authenticate remote agents by itself or replace scoped workload identity, signed permits, SPARTa routing, Decision Lifecycle Ledger evidence, or customer-specific policy.

## Scoring Invariants

`reference_engine/scoring_invariants.py` verifies declared safety properties for the recoverability and Model/Agent Fitness scoring formulas. The report checks monotonic behavior, fail-closed executor qualification, and the separation between hard constraints and softer ranking signals.

```bash
python -m reference_engine.scoring_invariants --pretty
python -m reference_engine.scoring_invariants \
  --json-output reports/scoring_invariants_results.json \
  --markdown-output reports/Scoring_Invariants_Report.md
python -m unittest tests.test_scoring_invariants -v
```

These invariants make score behavior more inspectable. They do not prove production incident reduction or customer-calibrated thresholds.

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

## SPARTa Router

`smerc.sparta-route.v1` turns a stored SMERC decision and a declared tool plan into a concrete route: execute, constrained execute, pause, block, require review, or block because escalation is unavailable. This is the first SPARTa component and sits between the decision engine and execution adapters.

```bash
python -m reference_engine.sparta_router \
  --decision examples/sparta/throttle_decision.json \
  --plan examples/sparta/github_actions_deploy_plan.json \
  --pretty
```

SPARTa v1 is intentionally conservative. If SMERC returns `THROTTLE` but the tool plan cannot apply scope limits, dry runs, checkpoints, or rollback as required, the router marks the plan non-executable and routes it to review. See `specification/SMERC_SPARTa_Router_v1.md`.

Adapters, coding agents, and review tools should also use `smerc.sparta-vocabulary.v1` for machine interpretation. It defines lifecycle verbs, route states, control verbs, evidence events, and failure reasons. Unknown vocabulary fails closed. See `specification/SMERC_SPARTa_Vocabulary_v1.md` and `examples/sparta/sparta_vocabulary.json`.

Route reports can optionally be signed with `smerc.sparta-route-signature.v1` HMAC metadata for pilot-grade tamper detection. This does not replace managed production key infrastructure or prove downstream enforcement. See `reports/signed_sparta_route_example.json`.

When a route is `REVIEW_REQUIRED`, the vendor-neutral human-review adapter can package the route into signed review request and response evidence:

```bash
python integrations/human_review/review_adapter.py verify-response \
  --review-request reports/human_review_request_example.json \
  --review-response reports/human_review_response_example.json \
  --request-secret development-human-review-request-secret \
  --response-secret development-human-review-response-secret \
  --pretty
```

This proves request/response binding before a live Slack, Teams, Jira, or ServiceNow delivery adapter exists. It does not prove external identity-provider assurance by itself.

The API can also route a stored decision by `replay_id`:

```bash
curl -X POST http://127.0.0.1:8788/v1/sparta/route \
  -H "Authorization: Bearer development-console-secret-2026-rotate" \
  -H "Content-Type: application/json" \
  --data '{"replay_id":"replay_...","adapter_id":"github-actions-deployer","action":"deploy_canary","requested_capability":"deployment","requested_scope_units":80,"side_effect_level":"external","metadata":{"workflow_run":"1001"}}'
```

## Control Mapping Library

`smerc.control-mapping-library.v1` maps abstract SMERC/SPARTa controls to declared native mechanisms and evidence requirements for a tool path.

```bash
python -m reference_engine.control_mapping \
  examples/control_mapping/github_actions_controls.json \
  --posture THROTTLE \
  --tool github_actions \
  --capability deploy_production \
  --controls limit_scope preview_before_execution require_rollback_plan preserve_replay \
  --pretty
```

The report is executable only when every requested control required for the selected posture is declared and supported by the selected tool. Unsupported or undeclared controls fail closed into review or blocking behavior. See `docs/Control_Mapping_Library.md` and `reports/Control_Mapping_Library_Example.md`.

## Governance Report Generator

`smerc.governance-report.v1` assembles existing SMERC artifacts into one replayable pilot review package.

```bash
python -m reference_engine.governance_report \
  examples/governance_report/github_actions_governance_bundle.json \
  --pretty
```

The generator cross-checks whether the decision posture matches the SPARTa route, the replay IDs agree, route controls are mapped or documented, missing controls are visible, and the Decision Lifecycle Ledger verifies. See `docs/Governance_Report_Generator.md` and `reports/Governance_Report_Example.md`.

## Decision Lifecycle Ledger

`smerc.decision-lifecycle-ledger.v1` records the complete governed life of one decision. It chains request, evidence, evaluation, human interaction, execution, delayed outcome, and learning recommendation records.

```bash
python -m reference_engine.decision_lifecycle_ledger \
  --example \
  --json-output reports/decision_lifecycle_ledger_example.json \
  --markdown-output reports/Decision_Lifecycle_Ledger_Example.md \
  --pretty
```

DLL is intentionally not an automatic learning system. It can recommend policy or calibration changes, but each learning recommendation remains `requires_review` until an accountable reviewer activates a policy through normal governance. See `docs/Decision_Lifecycle_Ledger.md`.

## DLL Intelligence

`smerc.dll-intelligence.v1` analyzes verified Decision Lifecycle Ledger records across a pilot. It surfaces near misses, harmful or helpful overrides, recurring missing evidence, rollback performance, recovery failures, governance drift signals, and review-gated policy recommendations.

```bash
python -m reference_engine.dll_intelligence \
  --example-bundle-output examples/decision_lifecycle_ledger_portfolio.json \
  --json-output reports/dll_intelligence_report.json \
  --markdown-output reports/DLL_Intelligence_Report.md \
  --pretty
```

DLL Intelligence is the governance memory layer: SMERC decides, SPARTa routes, DLL records, and DLL Intelligence asks what the organization is learning across decisions. It does not silently retrain models or activate policy. See `docs/DLL_Intelligence.md` and `reports/DLL_Intelligence_Report.md`.

## End-To-End PR Guardian Demo

`smerc.end-to-end-pr-guardian-demo.v1` connects the current runtime pieces into one pilot-grade proof loop for an AI-assisted pull request:

```text
AI-assisted PR request -> SMERC decision -> PR Guardian comment/certificate -> SPARTa route -> Decision Lifecycle Ledger -> DLL Intelligence
```

```bash
python -m reference_engine.end_to_end_pr_guardian_demo --pretty
```

The command writes a CISO-readable report and machine-readable artifacts under `reports/`. See `docs/End_To_End_PR_Guardian_Demo.md` and `reports/End_To_End_PR_Guardian_Demo.md`.

The report includes local proof-loop latency measurements for decision evaluation, PR artifact rendering, SPARTa routing, DLL creation, and DLL Intelligence analysis. Treat these as operational-overhead checks, not as production performance evidence.

This is synthetic integration proof, not customer production evidence.

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
python -m reference_engine.constraint_eligibility examples/constraint_eligibility/prohibited_audit_log_delete.json --pretty
python -m reference_engine.github_actions_pilot_installer --output-dir reports/github_actions_pilot_package --pretty
python -m reference_engine.mcp_proxy_runner --request examples/mcp/tool_call_delete_customer_records.json --mode enforce --pretty
python -m reference_engine.mcp_proxy_runner --request examples/mcp/tool_call_search_docs.json --mode enforce --require-agent-identity --pretty
python -m reference_engine.mcp_transport_proxy --envelope examples/mcp/transport_proxy_delete_customer_records.json --require-agent-identity --pretty
python -m reference_engine.mcp_governance_gateway --mode enforce --pretty
python -m reference_engine.self_service_pilot_connector --bundle examples/self_service_pilot_bundle.json --pretty
python -m reference_engine.content_evidence --pretty
python -m reference_engine.fallback_policy --pretty
python -m reference_engine.recoverability_engine examples/recoverability_single_action.json --pretty
python -m reference_engine.sparta_router --decision examples/sparta/throttle_decision.json --plan examples/sparta/github_actions_deploy_plan.json --pretty
python -m reference_engine.sparta_conformance examples/sparta/adapter_registry.json --pretty
python -m reference_engine.control_mapping examples/control_mapping/github_actions_controls.json --posture THROTTLE --tool github_actions --capability deploy_production --controls limit_scope preview_before_execution require_rollback_plan preserve_replay --pretty
python -m reference_engine.governance_report examples/governance_report/github_actions_governance_bundle.json --pretty
python -m reference_engine.decision_lifecycle_ledger --example --pretty
python -m reference_engine.end_to_end_pr_guardian_demo --pretty
python -m reference_engine.smerc_f_profile_packet examples/financial_action_requests.json --policies conservative balanced permissive --pretty
python -m reference_engine.runtime_benchmark_suite examples/proxy_incident_replay_scenarios.json --pretty
python -m reference_engine.benchmark_ledger_builder reports/runtime_governance_benchmark.json --pretty
python -m reference_engine.pilot_ledger_intake reports/runtime_benchmark_dll_bundle.json examples/pilot_ledger_intake_example.json --decision-id "dll:proxy-deploy-001::baseline" --pretty
python -m reference_engine.pilot_ledger_metrics reports/pilot_ledger_intake_result.json --pretty
python -m reference_engine.github_actions_pilot_summary test_outputs/github_action_remote
python -m reference_engine.design_partner_fit examples/design_partner_fit_example.json --pretty
python -m reference_engine.first_pilot_packet --pretty
python -m reference_engine.public_discovery_audit ../SMERC-Macro-Language-Model/site --pretty
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

Run the pre-scoring admission gate first when testing hard gates:

```bash
curl -X POST http://127.0.0.1:8788/v1/admission/evaluate \
  -H "Authorization: Bearer development-console-secret-2026-rotate" \
  -H "Content-Type: application/json" \
  --data @examples/runtime_admission_request.json
```

Call the same authenticated API from Python:

```python
import json
from pathlib import Path

from smerc_sdk import SMERCClient

client = SMERCClient(
    "http://127.0.0.1:8788",
    token="development-console-secret-2026-rotate",
)
action = json.loads(Path("examples/recoverability_single_action.json").read_text())
decision = client.evaluate(action, idempotency_key="workflow-run-1001")
print(decision["posture"], decision["replay_id"])
```

See `docs/Python_SDK_Quickstart.md` for replay, review, metrics, and queue examples.

Call the same authenticated API from JavaScript:

```js
import { readFile } from 'node:fs/promises';
import { SMERCClient } from './smerc_js_sdk/index.mjs';

const client = new SMERCClient('http://127.0.0.1:8788', {
  token: 'development-console-secret-2026-rotate',
});
const action = JSON.parse(await readFile('examples/recoverability_single_action.json', 'utf8'));
const decision = await client.evaluate(action, { idempotencyKey: 'workflow-run-1001' });
console.log(decision.posture, decision.replay_id);
```

See `docs/JavaScript_SDK_Quickstart.md` for replay, review, metrics, and queue examples.

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

Generate the proxy incident-replay benchmark:

```bash
python -m reference_engine.proxy_evidence_benchmark \
  examples/proxy_incident_replay_scenarios.json \
  --json-output reports/proxy_incident_replay_benchmark.json \
  --markdown-output reports/Proxy_Incident_Replay_Benchmark.md
```

This benchmark is scenario-based proxy evidence. It is useful for review and hypothesis testing; it is not production validation or a claim that SMERC reduces incidents in live environments.

Run the browser-based pilot review console:

```bash
export SMERC_CORS_ORIGINS="http://127.0.0.1:8790"
python -m http.server 8790 --bind 127.0.0.1 --directory pilot_console
```

Open `http://127.0.0.1:8790` and connect it to the authenticated API. The bearer key remains in memory for that tab; the console uses no browser storage, cookies, analytics, or third-party assets. It can also generate stored DLL evidence packages for CISO review when the principal has `audit.read`. See `pilot_console/README.md`.

Run the GitHub Actions gate locally:

```bash
python integrations/github_actions/run_smerc_gate.py \
  --action-file integrations/github_actions/sample_action_request.json \
  --mode observe \
  --output-file smerc-decision.json
```

The GitHub Action can also call the authenticated `/v1/evaluate` endpoint. Remote mode supports an exact GitHub OIDC trust policy or the static `SMERC_API_KEY` compatibility path, requires HTTPS outside loopback tests, reuses an idempotency key across evaluation retries, and fails closed in enforce mode. See `integrations/github_actions/README.md`.

Render a SMERC PR Guardian comment and certificate:

```bash
python integrations/github_pr_guardian/pr_guardian.py \
  --decision-report smerc-decision.json \
  --action-file integrations/github_actions/sample_action_request.json \
  --comment-output smerc-pr-comment.md \
  --certificate-output smerc-pr-certificate.json
```

PR Guardian is the visible pull-request review surface for AI-assisted changes. It turns a SMERC decision into posture, risk, confidence, replay ID, reason codes, controls, and a hash-bound certificate digest that can be posted as a PR comment. See `docs/GitHub_PR_Guardian.md`, `integrations/github_pr_guardian/README.md`, and `examples/github_pr_guardian/pr_guardian_workflow.yml`.

Generate a synthetic GitHub Actions shadow-mode pilot report:

```bash
python -m reference_engine.pilot_report \
  examples/github_actions_shadow_mode_scenarios.json \
  --json-output reports/github_actions_shadow_mode_results.json \
  --markdown-output reports/GitHub_Actions_Shadow_Mode_Pilot_Report.md
```

Summarize downloaded `smerc-decision.json` artifacts from an actual GitHub Actions pilot:

```bash
python -m reference_engine.github_actions_pilot_summary downloaded-smerc-decisions \
  --json-output reports/github_actions_pilot_artifact_summary.json \
  --markdown-output reports/GitHub_Actions_Pilot_Artifact_Summary.md
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

Run the optional Financial Runtime Governance profile, internally called SMERC-F:

```bash
python -m reference_engine.financial_permission_profile \
  examples/financial_action_requests.json --policy balanced --pretty
```

Run the financial runtime historical-context replay suite:

```bash
python -m reference_engine.financial_replay \
  examples/financial_replay_scenarios.json \
  --report reports/SMERC_F_Replay_Report.md
```

Run the financial runtime public-data replay harness:

```bash
python -m reference_engine.smerc_f_public_data_replay \
  examples/smerc_f_public_data_replay_inputs.json \
  --pretty
```

The public-data replay harness expands 10 public-data-shaped source rows into 50 replay scenarios. It is useful for showing ingestion, transformation, posture, reason codes, and report shape. It is not customer validation, address attribution, AML screening, sanctions screening, transaction monitoring, custody, settlement, payment execution, incident-prevention proof, or production certification.

The generated report includes a financial reason-code layer and Work / Result / Impact examples so banks, fintechs, stablecoin operators, and treasury teams can see whether recoverability changes pre-execution judgment.

Run the financial runtime source ingestion adapter:

```bash
python -m reference_engine.smerc_f_source_ingestion \
  examples/smerc_f_source_exports.json \
  --pretty
```

The source ingestion adapter accepts Dune-, BigQuery-, Chainabuse-, DefiLlama-, and Elliptic-shaped exported metadata, normalizes it into SMERC-F replay rows, and regenerates the replay report. It does not call live vendor APIs, enrich addresses, determine illicit activity, move funds, or certify financial controls.

Run the financial runtime external signal adapter:

```bash
python -m reference_engine.smerc_f_external_signals \
  examples/smerc_f_external_signal_examples.json \
  --pretty
```

The external signal adapter accepts AML/KYT-, wallet-screening-, fraud-, Travel Rule-, treasury-risk-, reserve-monitoring-, blockchain-analytics-, transaction-monitoring-, and smart-contract-risk-style outputs, normalizes them into SMERC-F recoverability fields, and reports where an existing `ALLOW`, `REVIEW`, or `ALERT` outcome should become `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE`. It does not call vendor APIs, perform AML or KYT screening, determine sanctions status, perform address attribution, satisfy Travel Rule obligations, move funds, execute transactions, or certify financial controls.

Run the financial runtime regulatory context overlay:

```bash
python -m reference_engine.smerc_f_regulatory_context --pretty
```

The regulatory context overlay uses legislation-inspired operational fields such as issuer status, reserve sensitivity, redemption pressure, custody dependency, lawful-order capability, jurisdiction complexity, customer-impact radius, and disclosure gaps to compare baseline replay with context-enriched replay. It does not interpret law, provide legal advice, determine compliance, screen AML or sanctions, classify illicit activity, move funds, or certify financial controls.

Run the financial runtime pilot evidence packet:

```bash
python -m reference_engine.smerc_f_pilot_evidence_packet --pretty
```

The pilot evidence packet combines the source-ingestion report, regulatory-context overlay, public-data replay, reviewer questions, go/no-go criteria, and claim boundaries into one financial-services review package. It is not AML compliance, legal compliance, fraud detection, sanctions screening, custody software, settlement infrastructure, payment execution, production certification, customer-demand proof, incident-reduction proof, or production-safety proof.

Run the Financial Runtime Customer Evaluation sample:

```bash
python -m reference_engine.customer_evaluation \
  examples/smerc_f_customer_eval_actions.json \
  --json-output reports/smerc_f_customer_evaluation/customer_evaluation_report.json \
  --markdown-output reports/smerc_f_customer_evaluation/Customer_Evaluation_Report.md \
  --pretty
```

The Financial Runtime Customer Evaluation path reuses the general customer-evaluation runner with finance-specific metadata-only actions. The internal profile name is SMERC-F. It is intended to help a financial-services reviewer decide whether a bounded shadow-mode review is justified before any production integration.

Run the Cloud Admin Customer Evaluation sample:

```bash
python -m reference_engine.customer_evaluation \
  examples/cloud_admin_customer_eval_actions.json \
  --json-output reports/cloud_admin_customer_evaluation/customer_evaluation_report.json \
  --markdown-output reports/cloud_admin_customer_evaluation/Customer_Evaluation_Report.md \
  --pretty
```

The Cloud Admin Customer Evaluation path reuses the general customer-evaluation runner with cloud-specific metadata-only actions. It is intended to help cloud security, SRE, platform, and infrastructure reviewers decide whether a bounded shadow-mode review is justified before any live cloud integration.

Run the Cloud Admin Proof Pack:

```bash
python -m reference_engine.cloud_admin_proof_pack --pretty
```

The Cloud Admin Proof Pack expands the eight cloud-admin examples into 24 metadata-only scenarios and reports cloud-specific reason codes, posture counts, SPARTa routes, valid DLL ledgers, autonomy-budget impact, and Work / Result / Impact examples. It is designed for infrastructure reviewers evaluating whether SMERC could help govern AI/devops agents before cloud actions change IAM, network boundaries, Kubernetes workloads, DNS, databases, secrets, capacity, or backup policy.

Run the Cloud Metadata Connector:

```bash
python -m reference_engine.cloud_metadata_connector examples/cloud_admin_source_exports.json --pretty
```

The Cloud Metadata Connector is the safer bridge from public proof to company evaluation. It converts read-only export summaries from IAM, Terraform, CloudTrail-style event summaries, Kubernetes rollout plans, DNS change requests, and backup-policy changes into strict SMERC customer-evaluation metadata. It does not call live cloud APIs, require credentials, read private infrastructure, or execute changes.

Run the Public Benchmark Ingestion Pack:

```bash
python -m reference_engine.public_benchmark_ingestion examples/public_benchmark_ingestion_examples.json --pretty
```

The Public Benchmark Ingestion Pack maps representative public benchmark-shaped examples into SMERC's customer-evaluation contract, then reports posture counts, SPARTa routes, Decision Lifecycle Ledger validity, and baseline-versus-SMERC deltas. It is adapter-ready proof for public governance benchmark categories; it is not an official score for any upstream benchmark until license-compatible datasets and documented runners are used.

Run the Postcondition Evidence report:

```bash
python -m reference_engine.postcondition_evidence \
  --evaluation reports/public_benchmark_customer_evaluation/customer_evaluation_report.json \
  --observations examples/postcondition_observations.json \
  --pretty
```

Postcondition Evidence compares SPARTa-required controls against observed control, execution, hold, and rollback evidence. It shows whether controls were actually observed after a route instead of only recommended before execution.

Run the Serious Report Performance harness:

```bash
python -m reference_engine.serious_report_performance --iterations 5 --pretty
```

Serious Report Performance measures local p50, p95, and maximum latency for major proof builders. It helps reviewers inspect evaluation cost, but it does not prove production latency, hosted API performance, throughput, SLA, customer workflow overhead, or reviewer burden.

Generate the Customer-Owned Metadata Request:

```bash
python -m reference_engine.customer_owned_metadata_request --workflow-family general --requested-actions 10 --pretty
```

This creates a safe request packet for external reviewers to replace public examples with 5 to 25 metadata-only actions from one real workflow. It is the next evidence step after public proof, benchmark ingestion, postcondition evidence, and local performance metrics.

Assess an external reviewer metadata response:

```bash
python -m reference_engine.external_reviewer_metadata_response examples/external_reviewer_metadata_response_example.json --pretty
```

This classifies reviewer-supplied metadata as `ready_for_customer_metadata_evaluation`, `ready_with_review_limits`, or `not_ready` before SMERC treats it as evidence.

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
- Public feedback: https://admirable-sorbet-9986d5.netlify.app/community.html
- Project status: https://admirable-sorbet-9986d5.netlify.app/status.html
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

> Does pre-execution recoverability control change reviewer judgment in a useful and repeatable way before AI-agent actions create side effects?

SMERC should be adopted only if a controlled pilot produces evidence that the answer is yes.

## License

See `LICENSE`.
