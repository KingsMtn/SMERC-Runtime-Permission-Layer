# Balanced Runtime Judgment Replay

## Purpose

The Balanced Runtime Judgment Replay shows that SMERC can distinguish between the full runtime posture ladder instead of acting like a simple allow/block filter.

It runs five metadata-only actions through the same customer-evaluation path:

- `ALLOW`: safe public read-only lookup
- `THROTTLE`: bounded external update that should execute only with constraints
- `FREEZE`: authorized action with unavailable recoverability evidence
- `DENY`: high-blast-radius destructive action with failed hard evidence gates
- `ESCALATE`: urgent security containment action that needs accountable review

## Run It

```bash
python -m reference_engine.balanced_runtime_judgment_replay examples/balanced_runtime_judgment_actions.json --pretty
```

Default outputs:

- `reports/Balanced_Runtime_Judgment_Replay_Report.md`
- `reports/balanced_runtime_judgment_replay_report.json`
- `reports/balanced_runtime_judgment_customer_evaluation/Customer_Evaluation_Report.md`
- `reports/balanced_runtime_judgment_customer_evaluation/customer_evaluation_report.json`

## Work / Result / Impact

Work: run safe, borderline, uncertain, harmful, and escalation-worthy actions through the same SMERC evaluation path.

Result: SMERC returns one `ALLOW`, one `THROTTLE`, one `FREEZE`, one `DENY`, and one `ESCALATE`, with valid Decision Lifecycle Ledger evidence for every action.

Impact: reviewers can see recoverability-aware judgment across the whole action lifecycle. This helps show SMERC is not trying to replace IAM or approval tools. It adds a pre-execution question: if an action is technically allowed, how much control does it need before it should proceed?

## Evidence Boundary

This is curated metadata-only proof. It is useful for reviewer understanding and threshold inspection, but it is not customer validation, production certification, a formal false-positive rate, or proof that thresholds are calibrated for a specific organization.

## Reviewer Question

Which posture is most useful to tune first for your workflow: `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE`?
