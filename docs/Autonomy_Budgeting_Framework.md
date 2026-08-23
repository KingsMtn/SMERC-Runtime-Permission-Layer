# Autonomy Budgeting Framework

## Purpose

Autonomy Budgeting answers:

> Given the situation right now, how much freedom should this system actually have?

SMERC evaluates individual actions. Autonomy Health evaluates whether an agent, workflow, or tool family is healthy enough to remain independent. Autonomy Budgeting converts those signals into a bounded allowance for continued autonomy.

## What Gets Budgeted

The reference model budgets:

- `max_actions`: how many actions or tool-call attempts can occur before review.
- `max_scope_units`: how much blast radius can be attempted during the session.
- `max_risk_spend`: how much cumulative pressure, posture severity, and ref-gate failure risk can be consumed.
- `valid_for_minutes`: how long the current autonomy grant remains valid.
- `allowed_tool_risk_tiers`: which tool classes remain available.

This is useful because safe autonomy is not binary. An agent may be allowed to read, simulate, or prepare work while being prevented from deleting data, moving money, or changing production.

## Budget Inputs

Autonomy Budgeting consumes:

- earned autonomy tier and starting budget context
- SMERC posture: `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE`.
- Gateway pressure: loop pressure, scope pressure, budget pressure, high-risk tool tier, and ref-gate drivers.
- Ref-gate status: typed contract, attestation, least privilege, and expected object shape.
- Requested scope units.
- Blocked or held attempt count.

Future pilot versions should also consume Decision Lifecycle Ledger outcomes, rollback success, reviewer agreement, incident severity, and override quality.

## Budget States

The operating states are:

- `HEALTHY`: autonomy remains within the current budget.
- `WATCH`: autonomy continues, but pressure is rising.
- `DEGRADE`: reduce tools, scope, action count, or review threshold.
- `SUSPEND_AUTONOMY`: remove autonomous execution until review.
- `REQUALIFY`: require owner review, policy update, or agent/tool validation before autonomy returns.

## Current Reference Behavior

The reference engine spends autonomy budget on every attempted action, not only successful actions. This is deliberate. Repeated unsafe attempts are operational signal even when SMERC blocks them.

The first implementation uses these rules:

- ref-gate failure suspends autonomy for the current session
- exhausted action, scope, or risk budget suspends autonomy
- repeated blocked or held attempts suspend autonomy
- high pressure or hard denies degrade autonomy
- moderate pressure moves autonomy to watch

Run:

```bash
python -m reference_engine.mcp_governance_gateway --mode enforce --pretty
python -m reference_engine.autonomy_budget --pretty
```

Generated outputs:

- `reports/mcp_governance_gateway_report.json`
- `reports/MCP_Governance_Gateway_Report.md`
- `reports/autonomy_budget_report.json`
- `reports/Autonomy_Budget_Report.md`
- `reports/earned_autonomy_report.json`
- `reports/Earned_Autonomy_Report.md`

## Commercial Meaning

Autonomy Budgeting gives a CISO, platform leader, or AI governance team a practical control:

> Do not only approve or block an agent. Meter its independence based on current evidence, pressure, recoverability, and behavior.

For a pilot, this can be measured by:

- how often budget shrinkage matches reviewer judgment
- how often budget exhaustion catches unsafe repeated attempts
- whether autonomy suspension reduces false release candidates
- whether degraded autonomy preserves useful low-risk work while blocking high-risk execution

Autonomy Continuance sits after the current budget decision and asks whether the actor still has the right to continue from the current point.

## Boundary

This is a reference model for shadow-mode evaluation. It is not a production entitlement service, IAM system, billing engine, legal compliance engine, or certified safety controller. Customer pilots must calibrate thresholds against real reviewer labels and operational outcomes.

See also `docs/Earned_Autonomy_Framework.md` and `docs/Autonomy_Continuance_Framework.md`.
