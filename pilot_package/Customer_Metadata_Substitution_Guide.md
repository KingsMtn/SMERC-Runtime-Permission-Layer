# Customer Metadata Substitution Guide

## Purpose

This guide explains how to replace SMERC sample inputs with customer-specific metadata before generating a core pilot package.

The goal is to create a realistic pilot package without collecting secrets, source code, customer records, private prompts, regulated payloads, or production logs.

## Inputs To Replace

The one-command core pilot package uses sample files by default:

```text
examples/core_prospect_route_sample.json
examples/customer_action_intake_sample.json
examples/pilot_handoff_checklist.json
examples/pilot_metrics_summary_sample.json
```

For a real prospect, copy these files to a customer-specific working folder and replace only the metadata fields.

Do not overwrite the public samples.

## Step 1: Prospect Route

Start from:

```text
examples/core_prospect_route_sample.json
```

Replace:

- organization
- organization type
- buyer title
- technical owner title
- workflow signals
- evidence statements

Use `true` only when the prospect explicitly confirms the condition.

Do not guess reviewer capacity, metadata readiness, observe-mode feasibility, or irreversible exposure.

## Step 2: Customer Action Intake

Start from:

```text
examples/customer_action_intake_sample.json
```

Replace the sample actions with 10 to 25 metadata-only actions from the prospect.

Each action should describe a proposed AI-agent, automation, or workflow action. The description should be specific enough for review but not include sensitive payloads.

Allowed examples:

- "AI deployment assistant proposes a production canary release."
- "Automation proposes broadening a cloud IAM role."
- "Support agent proposes sending an outage email to all customers."

Do not include:

- code bodies
- secrets
- customer names
- account numbers
- private prompts
- incident details
- transaction payloads
- regulated records

## Step 3: Pilot Handoff

Start from:

```text
examples/pilot_handoff_checklist.json
```

Set each required item to `yes` only if the prospect has confirmed it.

If any item is not confirmed, use `no` and explain the gap in the evidence field.

Do not start observe-mode setup until all required handoff items are `yes`.

## Step 4: Pilot Metrics

Before a pilot runs, omit `--pilot-metrics`.

After reviewer-labeled pilot records exist, provide a metrics file shaped like:

```text
examples/pilot_metrics_summary_sample.json
```

Do not use sample metrics in external claims. Replace them with customer-observed reviewer metrics.

## Step 5: Generate The Package

Run with prospect-specific files:

```bash
python -m reference_engine.core_pilot_package \
  --prospect-route customer_working/prospect_route.json \
  --customer-intake customer_working/customer_action_intake.json \
  --pilot-handoff customer_working/pilot_handoff.json \
  --output-dir reports/customer_working_core_pilot_package \
  --pretty
```

After reviewer-labeled metrics exist:

```bash
python -m reference_engine.core_pilot_package \
  --prospect-route customer_working/prospect_route.json \
  --customer-intake customer_working/customer_action_intake.json \
  --pilot-handoff customer_working/pilot_handoff.json \
  --pilot-metrics customer_working/pilot_metrics_summary.json \
  --output-dir reports/customer_working_core_pilot_package \
  --pretty
```

## Review The Output

Start with:

```text
reports/customer_working_core_pilot_package/README.md
```

Then review:

- `prospect-route.md`
- `customer-action-intake.md`
- `pilot-evidence-summary.md`
- `pilot-handoff.json`

## Safe Language

Say:

> This package uses metadata-only examples supplied for pilot review.

Do not say:

> This proves SMERC reduces incidents.

Say:

> The next step is observe-mode scoring if the handoff gate is complete.

Do not say:

> SMERC is ready to block production workflows.

## Boundary

Customer metadata substitution is pilot preparation. It is not production certification, compliance attestation, customer demand proof, incident-reduction proof, or legal approval for enforcement.
