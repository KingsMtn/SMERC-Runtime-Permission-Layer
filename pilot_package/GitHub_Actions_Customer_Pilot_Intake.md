# GitHub Actions Customer Pilot Intake

## Purpose

This packet is what an interested company should complete before SMERC starts week-zero pilot qualification.

It answers one operational question:

> Can this customer safely provide metadata for one GitHub Actions workflow so SMERC can run in observe mode and compare output with reviewer judgment?

This is not a sales contract, production approval, legal approval, or enforcement authorization.

## What To Fill Out

Start from:

```text
examples/github_actions_customer_pilot_intake_packet.json
```

Replace the example organization and workflow details with customer-specific metadata.

Keep the packet metadata-only. Do not include:

- secrets
- credentials
- raw source code
- customer records
- private prompts
- regulated payloads
- full incident logs
- production database output

## Required Customer Answers

The packet asks for:

- selected repository or workflow family
- workflow name and triggers
- existing controls
- workflow side effects
- approved metadata fields
- excluded data fields
- retention period
- security owner
- platform owner
- reviewer group
- stop conditions
- weekly review commitment
- day-30 go/no-go criteria
- 10 to 25 sample action descriptions

The sample actions should be plain-language descriptions of proposed workflow actions. They should not include payloads.

Good examples:

- "AI deployment assistant proposes production canary release."
- "Automation proposes database migration with rollback plan."
- "AI code agent proposes permission change in deployment workflow."

## Run The Intake Check

```bash
python -m reference_engine.github_actions_customer_pilot_intake \
  examples/github_actions_customer_pilot_intake_packet.json \
  --pretty
```

Generated outputs:

```text
reports/github_actions_customer_pilot_intake_report.json
reports/GitHub_Actions_Customer_Pilot_Intake_Report.md
```

## Readiness Meaning

`ready_for_review_call: true` means the packet is complete enough for a review call.

`ready_for_week_zero: true` means there are no blockers or warnings from this screen.

Warnings do not always prevent a technical review. They often identify commercial or ownership gaps that should be resolved before a paid pilot.

## What Happens Next

If the packet is ready for a review call:

1. Review the workflow and side effects with the customer.
2. Convert the 10 to 25 sample descriptions into `smerc.customer-action-intake.v1` metadata.
3. Run `reference_engine.customer_action_intake`.
4. Complete `pilot_package/Pilot_Handoff_Checklist.md`.
5. Start observe-mode setup only when owners, reviewers, boundary, metrics, and stop conditions are confirmed.

## Stop Conditions

Do not continue if:

- metadata-only boundary is not confirmed
- enforcement is requested before shadow-mode calibration
- existing approvals will not remain authoritative
- security owner is not confirmed
- platform owner is not confirmed
- reviewer group is not confirmed
- stop conditions are missing
- weekly review is not confirmed
- day-30 go/no-go criteria are missing
- fewer than 10 sample actions are available

## Evidence Boundary

Customer pilot intake is preparation only.

It does not prove buyer demand, customer validation, production safety, incident reduction, compliance, or approval for enforcement.
