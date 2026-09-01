# SMERC Category Positioning

## Position

SMERC should be described first as:

> Pre-execution recoverability control for AI agents and high-impact automation.

The technical implementation category remains:

> Recoverability-aware runtime permission infrastructure.

## Why This Is Sharper

`Runtime governance` is broad. Many systems can claim it.

SMERC's specific control point is narrower:

> Before an authorized automated action executes, SMERC checks whether it can be recovered, constrained, paused, escalated, or blocked.

That makes the product easier to compare with adjacent systems:

- IAM and policy systems decide whether an actor or workflow has authority.
- AI gateways and guardrails inspect prompts, outputs, model calls, or content risk.
- Sandboxes limit where agents can run.
- Approval tools route human review.
- SMERC adds a pre-execution recoverability control at the action boundary.

## Public Wording

Use this first:

> SMERC is a pre-execution recoverability control layer for AI agents, MCP tool calls, GitHub Actions, cloud automation, financial actions, and other high-impact workflows.

Use this second:

> The reference implementation is runtime permission infrastructure that returns `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE` before execution.

## Financial Wording

For SMERC-F, use:

> Financial pre-execution recoverability control for automated payment, treasury, stablecoin, wallet-policy, reserve-status, and tokenized-finance actions.

SMERC-F can consume AML/KYT, wallet-screening, fraud, Travel Rule, treasury-risk, reserve-monitoring, blockchain-analytics, transaction-monitoring, and smart-contract-risk outputs as evidence. It does not replace those systems.

## Boundary

This is a positioning improvement, not new proof of product-market fit.

It does not prove buyer demand, live incident reduction, compliance readiness, patentability, production performance, or customer willingness to pay.
