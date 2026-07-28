# Customer Action Intake

## Purpose

Customer action intake is the first practical bridge from public review to a real pilot.

A prospect can provide metadata-only examples of actions their AI agents, automations, or workflows may attempt. SMERC scores those actions and produces a review report showing posture decisions, recoverability signals, metadata gaps, and pilot fit.

## Data Boundary

Do not include:

- secrets
- credentials
- source code
- customer records
- private logs
- production database output
- confidential incident details

Include only action metadata:

- action description
- actor or automation type
- tool or workflow family
- risk estimates
- reversibility estimates
- containment and rollback estimates
- evidence quality
- anomaly pressure
- impact scope

## Run

```bash
python -m reference_engine.customer_action_intake examples/customer_action_intake_sample.json --pretty
```

Generated outputs:

```text
reports/customer_action_intake_report.json
reports/Customer_Action_Intake_Report.md
```

## How To Use The Report

Use the report in a review call to answer:

1. Which actions create the highest irreversible exposure?
2. Which actions are constrained or escalated instead of simply allowed or blocked?
3. Which metadata is missing before a shadow-mode pilot?
4. Would human reviewers agree with the posture?
5. Is there a side-effecting workflow worth testing in observe mode?

## Pilot Gate

Move to a pilot only when:

- the prospect can provide realistic metadata-only action samples
- a security, platform, or governance reviewer can label decisions
- at least one side-effecting workflow has meaningful recoverability risk
- observe mode can run without changing production behavior

Do not move to enforcement based on intake scoring alone.
