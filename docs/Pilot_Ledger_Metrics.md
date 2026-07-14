# Pilot Ledger Metrics

Pilot Ledger Metrics summarizes completed SMERC Decision Lifecycle Ledger evidence.

It is designed for design-partner pilots where SMERC needs to show what evidence has been collected, what reviewers did, what executed, what happened afterward, and what still cannot be claimed.

## Inputs

The metrics engine accepts:

- pilot ledger intake result JSON files
- raw DLL JSON files

Every ledger must verify before it is summarized.

## Metrics

The report calculates:

- valid ledger count
- complete lifecycle count
- human review count
- reviewer agreement rate
- reviewer override rate
- execution success rate
- rollback rate
- outcome review count
- judged-correct rate
- unexpected consequence rate
- control sufficiency rate
- learning recommendation count

All rates disclose denominators. If no denominator exists, the rate is reported as unavailable rather than invented.

## Example

```bash
python -m reference_engine.pilot_ledger_metrics \
  reports/pilot_ledger_intake_result.json \
  --json-output reports/pilot_ledger_metrics.json \
  --markdown-output reports/Pilot_Ledger_Metrics_Report.md \
  --pretty
```

## Evidence Boundary

This report is evidence accounting. It is not proof of production incident reduction.

Small samples, synthetic examples, incomplete lifecycles, and customer-specific workflow differences must be disclosed before the report is used in a CISO or design-partner review.
