# Earned Autonomy Framework

## Purpose

Earned Autonomy answers:

> What has this agent, workflow, tool family, or team proven over time, and has it earned more independence?

Autonomy Budgeting controls current freedom. Earned Autonomy determines the starting allowance based on prior evidence.

## Operating Principle

Unproven systems start constrained. Clean history can earn limited additional freedom. Bad history removes freedom until review.

```text
Decision history -> Earned tier -> Starting autonomy budget -> Current session behavior -> Budget shrinkage or suspension
```

## Earned Autonomy Tiers

- `TIER_0_OBSERVE`: no autonomous execution because there is not enough history.
- `TIER_1_ASSIST`: recommendations only or one tightly scoped low-risk action.
- `TIER_2_CONSTRAINED`: limited low/medium-risk tool use with small scope and short validity.
- `TIER_3_BOUNDED`: broader autonomy within budget for systems with clean operating history.
- `TIER_4_TRUSTED`: higher allowance for systems with large clean history, high reviewer agreement, and low override rate.
- `TIER_5_REQUALIFY_REQUIRED`: autonomy revoked pending review because history contains disqualifying evidence.

## Evidence Inputs

The reference engine evaluates:

- total prior decisions
- successful executions
- reviewer agreement rate
- human override rate
- ref-gate failure rate
- rollback success rate
- false release rate
- incident count
- near-miss count
- scope violation count
- evidence gap rate

## Disqualifying Evidence

The reference model requires requalification when prior evidence contains:

- any incident or false release
- repeated ref-gate failures
- scope violations
- material evidence gaps

Those are not treated as soft negatives. They prevent autonomy expansion until the agent or workflow is reviewed.

## Relationship To Autonomy Budgeting

Earned Autonomy sets the starting budget context:

- lower tiers start with fewer actions, smaller scope, lower risk spend, and fewer tool tiers
- higher tiers start with more actions, larger scope, higher risk spend, and broader tool tiers
- `TIER_5_REQUALIFY_REQUIRED` starts with no autonomous budget

Current behavior can still reduce or remove autonomy. A `TIER_3_BOUNDED` system can lose session autonomy if it exceeds scope, triggers repeated denies, or fails a ref gate.

## Run

```bash
python -m reference_engine.earned_autonomy --pretty
python -m reference_engine.mcp_governance_gateway --mode enforce --pretty
```

Generated outputs:

- `reports/earned_autonomy_report.json`
- `reports/Earned_Autonomy_Report.md`
- `reports/mcp_governance_gateway_report.json`
- `reports/MCP_Governance_Gateway_Report.md`

## Boundary

Earned Autonomy is a reference model for pilot evaluation. It is not a production trust score, employee score, legal compliance rating, insurance rating, or automated personnel-management system. Real deployments must calibrate tiers with customer-owned review labels, operational outcomes, and governance approval.
