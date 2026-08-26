# Expected SMERC Evaluation Report

A company should expect the generated report to include these sections.

## 1. Evidence Boundary

States that the evaluation is metadata-only and does not prove production safety, compliance, incident reduction, customer demand, or enforce-mode readiness.

## 2. Workflow Context

Names the selected workflow family and the data boundary used for review.

## 3. Summary

Includes:

- total actions evaluated
- Ref-gate counts
- posture counts
- route-state counts
- non-executable route count
- valid Decision Lifecycle Ledger count
- autonomy state
- pilot-fit recommendation

## 4. Highest Exposure Actions

Shows the actions with the highest irreversible exposure scores.

## 5. Decision Path

Shows each action across:

- hard gate result
- scoring admission
- SMERC posture
- SPARTa route
- executable state
- ledger validity

## 6. Action Details

For each action:

- description
- failed hard gates, if any
- reason codes
- scores
- recommended controls
- execution route
- ledger validity

## 7. Autonomy Budget

Shows whether the evaluated action stream should continue operating normally, reduce autonomy, hold, or require requalification.

## 8. Recommended Next Action

Recommends one of:

- move to review call
- collect stronger workflow metadata
- do not propose pilot yet

