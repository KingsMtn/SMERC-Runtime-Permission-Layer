# Accelerator And Adjacent Company Map

## Purpose

This map records the honest market reality around SMERC for accelerator, strategic partner, and technical reviewer conversations.

The goal is not to claim that no one else is working on agent governance. The goal is to show exactly where SMERC overlaps existing work, where it differs, and what evidence is needed before SMERC should be pitched as more than a promising pilot-grade artifact.

## Blunt Finding

The market is already active.

YC has backed companies close to AI-agent authorization, MCP infrastructure, sandboxes, agent runtime security, observability, and governance. That is a positive signal that the category matters, but it also means SMERC cannot rely on novelty alone.

MACH37 appears more aligned as a credibility and cyber-review path because its public portfolio is broader across cybersecurity and AI security, with fewer visible exact clones of recoverability-aware pre-execution governance.

## Adjacent Company Categories

| Category | What They Usually Do | SMERC Difference |
| --- | --- | --- |
| Agent authorization | Decide which agent can call which tool or API. | SMERC asks whether the specific action is recoverable enough to execute now. |
| MCP infrastructure | Connect agents to tools, data, workflows, and enterprise systems. | SMERC can sit at the tool-call boundary and score action consequence before execution. |
| Agent sandboxes | Run code or agents in controlled environments. | SMERC adds posture, route controls, and lifecycle evidence around whether the action should proceed. |
| AI gateways | Filter prompts, outputs, model calls, and content risk. | SMERC focuses on action permission, not only content or model input/output safety. |
| Policy engines | Evaluate declarative policy. | SMERC adds recoverability, evidence trust, consequence horizon, autonomy state, and replayable outcomes. |
| Approval workflows | Route human approval requests. | SMERC decides when approval is needed and preserves why the route was chosen. |
| Audit/logging systems | Record what happened. | SMERC records request, evidence, decision, override, execution, outcome, and learning recommendations. |

## YC-Relevant Overlap

YC-backed and YC-adjacent companies already support parts of the agent governance stack:

- secure agent access control
- fine-grained authorization
- agent guardrails
- MCP governance
- tool-call control
- sandboxed execution
- credentials and secrets handling
- observability
- trace and audit logs
- enterprise integrations

That means SMERC should not pitch itself as the only runtime governance idea.

It should pitch this:

> SMERC complements agent authorization, MCP infrastructure, AI gateways, and sandboxes by adding recoverability before execution and a complete decision lifecycle record.

## MACH37-Relevant Fit

MACH37 is a better near-term credibility target if the goal is cyber-sector review rather than direct comparison with several YC-backed agent-infrastructure companies.

The stronger MACH37 framing is:

> SMERC is a pilot-grade runtime permission layer for recoverability-aware AI-agent and automation governance. We are seeking cyber reviewers who can test whether recoverability before execution changes judgment on real but metadata-only workflows.

## What This Changes

SMERC should build and present itself as:

- a recoverability checkpoint, not a generic AI firewall
- an action-governance layer, not a model safety tool
- a complement to agent authorization and MCP infrastructure, not a replacement
- a shadow-mode pilot system first, not a production enforcement platform
- an evidence generator for reviewers, not a finished enterprise platform

## Evidence Needed To Compete

Before SMERC is credible against stronger funded companies, it needs:

- one external technical reviewer who confirms the concept is useful
- one company-owned metadata test with 5 to 25 actions
- reviewer agreement and disagreement notes
- examples where SMERC created useful middle states instead of simple allow/deny
- examples where SMERC was wrong or too conservative
- measured setup burden
- measured report usefulness
- a clear stop condition if reviewers do not care

## Best Outreach Question

Use this question with accelerators, CISOs, platform teams, and agent-governance communities:

> Does recoverability before execution belong as a first-class control for agent and automation governance, or should it remain a secondary signal inside existing authorization and approval systems?

## Boundary

This map is not a competitive legal opinion, market-size analysis, patent assessment, endorsement, or proof that SMERC can beat funded companies.

It is an operating guide for keeping SMERC honest while building toward external validation.
