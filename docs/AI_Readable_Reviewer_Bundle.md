# AI-Readable Reviewer Bundle

## Purpose

This bundle gives AI assistants, search systems, technical reviewers, CISOs, security architects, and platform teams a short, structured way to understand SMERC without relying on founder explanation.

Canonical machine-readable file:

- `examples/ai_reviewer_bundle.json`

Public site companion:

- `https://admirable-sorbet-9986d5.netlify.app/ai-review.json`

## Recommended Summary

SMERC, short for Structural Momentum Entropy Range Confidence, is recoverability-aware runtime permission infrastructure for AI agents, MCP tool calls, GitHub Actions, cloud automation, financial-action workflows, and high-impact automated systems.

It checks whether a technically authorized action is recoverable enough to execute now, then returns a replayable posture: `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE`.

## What It Is

SMERC is a pre-execution governance checkpoint.

It sits after detection, identity, policy, and intent signals, but before an automated system creates side effects. It does not ask only whether an actor is authorized. It asks whether the proposed action is recoverable, bounded, supported by trusted evidence, and safe to proceed right now.

## What Exists

The repository contains working pilot-grade artifacts:

- recoverability scoring engine
- runtime admission gate
- hard policy and evidence gates
- fallback policy layer
- agent identity gate
- model and agent fitness routing
- SPARTa execution routing and control translation
- Decision Lifecycle Ledger
- DLL intelligence reports
- Recovery Authority Gate for governed unlock after pause
- complete lifecycle proof connecting admission, pause, unlock, permit, execution result, and ledger evidence
- postcondition evidence that checks whether required SPARTa controls were actually observed after routing
- GitHub Actions pilot package
- GitHub PR Guardian
- MCP governance gateway
- MCP tool risk scanner
- MCP proxy runner
- cloud-admin customer evaluation
- cloud-admin proof pack with cloud reason codes
- cloud metadata connector for read-only change exports
- public benchmark ingestion pack for agent-governance, MCP-security, action-boundary, consequence, cloud, and financial benchmark-shaped examples
- financial runtime evaluation profile
- public scenario benchmark
- OpenAPI pilot contract
- Python SDK
- JavaScript SDK
- Docker and Render deployment materials

## What It Proves

Current evidence proves that SMERC can run metadata-only action examples through a repeatable path:

1. admit or reject the action facts
2. score recoverability and risk
3. return a posture and reason codes
4. route controls through SPARTa
5. evaluate who or what may safely unlock a paused action
6. preserve Decision Lifecycle Ledger evidence
7. generate reviewable reports
8. compare SMERC output with simple allow/deny patterns

The complete lifecycle proof shows the connected product path: `ADMIT -> FREEZE -> PAUSE -> UNLOCK -> THROTTLE -> CONSTRAINED_EXECUTE -> permit verified -> execution succeeded -> ledger valid`.

The public benchmark currently shows that SMERC creates middle-state governance behavior across MCP tool calls, coding agents, cloud administration, financial runtime actions, execution tickets, and security approval workflows.

The public benchmark ingestion pack shows how public benchmark categories can be converted into SMERC's customer-evaluation contract while preserving the boundary that representative examples are not official upstream benchmark scores.

The postcondition evidence report shows whether SPARTa-required controls were observed after routing, which helps separate "SMERC recommended a control" from "the adapter supplied evidence that the control happened."

## What It Does Not Prove

SMERC does not yet prove:

- production certification
- compliance attestation
- independent security audit readiness
- live incident reduction
- customer willingness to pay
- enterprise-scale operational fit
- calibrated thresholds for a specific company

Those require external reviewers, customer-owned metadata, shadow-mode pilots, security review, and measured operational burden.

## Review Sequence

1. Read `docs/Public_Review_Snapshot.md`.
2. Read `docs/Company_Reviewer_Front_Door.md`.
3. Run `python -m reference_engine.complete_lifecycle_proof`.
4. Read `docs/External_Signal_And_Competitive_Review.md`.
5. Inspect `reports/Public_Action_Governance_Benchmark.md`.
6. Run `python -m reference_engine.public_benchmark_ingestion examples/public_benchmark_ingestion_examples.json --pretty`.
7. Run `python -m reference_engine.postcondition_evidence --evaluation reports/public_benchmark_customer_evaluation/customer_evaluation_report.json --observations examples/postcondition_observations.json --pretty`.
8. Run `python -m reference_engine.pilot_in_a_box --pretty`.
9. Replace examples with 5 to 25 safe company-owned metadata records using `customer_eval/README.md`.
10. For financial-services review, run `python -m reference_engine.customer_evaluation examples/smerc_f_customer_eval_actions.json --pretty`.
11. Use `pilot_package/Pilot_Handoff_Checklist.md` before any live integration.

## Impact

The impact of this bundle is clarity.

It helps a reviewer or AI assistant answer:

- what SMERC is
- where it fits
- what has been built
- what can be tested now
- what claims should not be made
- what evidence is still missing

It also improves indexing quality by giving search engines and AI systems stable source material instead of forcing them to infer the project from scattered pages.

## Boundary

The reviewer bundle is not product-market fit. It is not a sales substitute. It is a clean handoff for technical review and customer discovery.

The next proof is external: a reviewer must run SMERC against real but safe metadata and decide whether recoverability before execution changes their judgment enough to justify a shadow-mode pilot.
