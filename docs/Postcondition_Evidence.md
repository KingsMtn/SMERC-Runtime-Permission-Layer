# Postcondition Evidence

## Purpose

Postcondition Evidence checks whether SMERC and SPARTa controls actually happened after a route decision.

SMERC should not only say:

> This action should be throttled, blocked, paused, or routed for review.

It should also preserve:

> Were the required controls observed, did execution follow the route, and what gaps remain?

## What It Does

The postcondition evidence runner compares:

- the SPARTa route state
- whether the route was executable
- the controls SPARTa required
- observed control evidence
- whether execution was attempted
- execution outcome
- rollback evidence if execution failed

Run it:

```bash
python -m reference_engine.postcondition_evidence \
  --evaluation reports/public_benchmark_customer_evaluation/customer_evaluation_report.json \
  --observations examples/postcondition_observations.json \
  --pretty
```

Generated outputs:

- `reports/Postcondition_Evidence_Report.md`
- `reports/postcondition_evidence_report.json`

## Work / Result / Impact

Work: compare required SPARTa controls against observed post-action or held-action evidence.

Result: the report identifies pass, gap, violation, and unobserved statuses for each routed action.

Impact: SMERC can show whether controls were actually observed after a route, not only whether it recommended them.

## Why This Matters

Many governance systems stop at approval, policy decision, ticket, or log.

Postcondition evidence moves SMERC one step further:

1. The action was proposed.
2. SMERC scored the action.
3. SPARTa routed the action.
4. Required controls were named.
5. Observed controls were compared against the route.
6. Gaps or violations were preserved for review.

That is important for CISOs, platform teams, SREs, financial operators, and AI-agent teams because a control that was recommended but never applied is not operational safety.

## Evidence Boundary

The checked-in example is metadata-only.

It proves accounting mechanics, not live enforcement.

Customer pilots should bind postcondition observations to native platform records or signed adapter evidence, such as:

- GitHub workflow run records
- deployment environment approvals
- cloud audit events
- Terraform plan and apply records
- MCP proxy forward or block events
- ticket or review records
- signed control evidence
- rollback records

## Reviewer Question

For the workflow you care about, can the adapter produce trustworthy evidence for each required control before the action is considered complete?
