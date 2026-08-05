# Fake Customer Production-Like Test

This test simulates a fake customer named AcmeCloud.

It exists to answer one narrow question:

> Can the SMERC reference build exercise a realistic customer-style workflow end to end without using a real customer environment?

The answer is yes, with an important boundary: this is production-like simulation, not production proof.

## What It Runs

The scenario file is:

- `examples/fake_customer_acme/production_like_scenarios.json`

The runner is:

- `reference_engine/fake_customer_pilot.py`

The generated evidence is:

- `reports/fake_customer_acme_pilot_report.json`
- `reports/Fake_Customer_Acme_Pilot_Report.md`

## Scenario Paths

The current package covers five paths:

- safe deployment
- risky production change
- destructive request
- escalated security request
- failure with rollback

Each path records:

- fake customer and repository
- traditional allow/deny outcome
- SMERC posture
- SPARTa route state
- simulated execution status
- recoverability scores
- reason codes
- controls
- Decision Lifecycle Ledger records

## Run It

```bash
python -m reference_engine.fake_customer_pilot \
  examples/fake_customer_acme/production_like_scenarios.json \
  --json-output reports/fake_customer_acme_pilot_report.json \
  --markdown-output reports/Fake_Customer_Acme_Pilot_Report.md
```

## What This Proves

- The recoverability engine can score fake customer actions.
- SMERC decisions can route through SPARTa.
- Safe, constrained, blocked, review-required, and rollback paths can be represented.
- Each scenario produces a valid Decision Lifecycle Ledger chain.
- The output can be reviewed as a pilot-style evidence package.

## What This Does Not Prove

- It does not prove real customer demand.
- It does not prove live production safety.
- It does not prove native GitHub runner isolation.
- It does not prove target-platform control truth.
- It does not prove incident reduction.
- It should not be described as customer validation.

Use this as a pre-customer program test before a real design-partner pilot.
