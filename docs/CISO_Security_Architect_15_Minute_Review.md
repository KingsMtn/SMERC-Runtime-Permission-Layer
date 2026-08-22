# SMERC CISO / Security Architect 15-Minute Review

## Purpose

This is the shortest serious review path for a CISO, security architect, platform security lead, or AI governance owner.

The review question is:

> Is SMERC credible enough to test in shadow mode against one real AI-agent, MCP tool-call, GitHub Actions, or automation workflow?

The review question is not:

> Is SMERC already a production-certified security platform?

## One-Sentence Positioning

SMERC is recoverability-aware runtime permission infrastructure that checks whether an automated action can safely proceed, be constrained, be paused, be denied, or be escalated before execution.

## What Problem It Solves

Existing controls usually answer:

- who or what is allowed to act
- whether a policy permits the action
- whether the request matches known security rules
- whether a workflow received approval

SMERC asks a different runtime question:

> If this action is wrong, unstable, poorly evidenced, or too broad, can the organization recover?

This matters for AI agents and automation because tool calls can create side effects faster than human review can inspect them.

## The 15-Minute Path

| Time | Review Step | Evidence |
| --- | --- | --- |
| 0-3 min | Understand the product claim and non-claims. | `README.md`, `docs/External_Review_Start_Here.md` |
| 3-6 min | Inspect the MCP runtime path. | `docs/MCP_Governance_Gateway.md`, `reports/MCP_Governance_Gateway_Report.md` |
| 6-9 min | Inspect the first practical pilot path. | `docs/GitHub_Actions_Pilot_Operator_Quickstart.md`, `pilot_package/First_Pilot_Path.md` |
| 9-12 min | Inspect replay and audit evidence. | `docs/Decision_Lifecycle_Ledger.md`, `reports/Governance_Report_Example.md` |
| 12-15 min | Decide whether a shadow-mode pilot is justified. | `pilot_package/GitHub_Actions_Customer_Pilot_Intake.md`, `docs/Pilot_Evaluation_Checklist.md` |

## What Exists Today

SMERC currently includes working code and reviewable artifacts for:

- recoverability scoring and posture decisions
- MCP tool-call governance
- MCP Governance Gateway session evaluation
- GitHub Actions observe-mode pilot path
- authenticated tenant-scoped REST API
- Decision Lifecycle Ledger evidence
- SPARTa route behavior and control mapping
- Python and JavaScript SDK helpers
- pilot review metrics and immutable review records
- SMERC-F financial-action profile materials
- generated reports and public GitHub Actions CI

## What The MCP Gateway Demonstrates

The MCP Governance Gateway is the clearest runtime proof surface because it sits where agents touch tools.

It evaluates:

- registered MCP tool definitions
- repeated tool-call pressure
- requested scope versus registry limits
- session-budget pressure
- action recoverability
- SMERC posture
- SPARTa route behavior
- proxy forward or block recommendation
- SMERC-F financial tool-family examples

The gateway does not implement OAuth, mTLS, native MCP transport, payment rails, wallet settlement, sandboxing, SIEM export, prompt-injection defense, or production billing.

## What A Reviewer Should Challenge

Challenge SMERC if:

- recoverability is already measured by an existing control in the target workflow
- action metadata cannot be trusted before execution
- reviewers cannot label false release, false constraint, useful constraint, and latency impact
- native tools cannot enforce the controls that SMERC recommends
- the organization expects production enforcement before shadow-mode evidence exists
- the workflow has no meaningful side effects or recoverability risk

## Pilot Decision

Proceed to a shadow-mode pilot only if:

- an AI agent or automation can trigger side effects
- the workflow can provide metadata without exposing secrets or regulated payloads
- a security, platform, or AI governance owner can review labels
- existing controls do not already answer recoverability clearly
- the pilot can run observe-only before enforcement

Reject or defer if:

- the organization only wants a certified production product
- the workflow lacks reliable metadata
- the buyer cannot identify a review owner
- the use case is only policy approval, not runtime action governance
- SMERC would duplicate an existing recoverability control without adding evidence

## First Recommended Pilot

Start with one GitHub Actions or MCP tool-call family in shadow mode.

Measure:

- posture distribution
- reviewer agreement
- false release candidates
- false constraint candidates
- useful constraints
- override reasons
- latency impact
- metadata gaps
- route/control coverage

## Bottom Line

SMERC is ready for CISO and security-architect review as a pilot-grade runtime permission layer.

It is not yet ready to claim production certification, compliance attestation, or proven live incident reduction.

