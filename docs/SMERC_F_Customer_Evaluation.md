# SMERC-F Customer Evaluation

## Purpose

SMERC-F Customer Evaluation is the metadata-only review path for financial-services teams that want to test recoverability-aware runtime permissioning before any pilot integration.

It is designed for automated financial actions such as refunds, payment retries, treasury rebalancing, stablecoin liquidity movement, tokenized collateral movement, wallet-policy changes, transaction-limit changes, and reserve-status publication.

It answers one practical question:

> If a financial-services reviewer provides safe metadata about proposed automated financial actions, does SMERC-F produce useful posture, routing, and audit evidence before execution?

## Run

From the repository root:

```bash
python -m reference_engine.customer_evaluation examples/smerc_f_customer_eval_actions.json --pretty
```

Generated files:

```text
reports/smerc_f_customer_evaluation/customer_evaluation_report.json
reports/smerc_f_customer_evaluation/Customer_Evaluation_Report.md
```

To write those files explicitly:

```bash
python -m reference_engine.customer_evaluation \
  examples/smerc_f_customer_eval_actions.json \
  --json-output reports/smerc_f_customer_evaluation/customer_evaluation_report.json \
  --markdown-output reports/smerc_f_customer_evaluation/Customer_Evaluation_Report.md \
  --pretty
```

## Run From GitHub Actions

Use the copyable workflow at:

```text
integrations/github_actions/customer_evaluation_workflow.yml
```

When running the workflow manually, set:

```text
action_file = examples/smerc_f_customer_eval_actions.json
```

The workflow uses read-only repository access and uploads the report artifact. It does not require SMERC API credentials, production credentials, wallet keys, payment credentials, or write access to financial systems.

## What The Sample Covers

The included SMERC-F customer-evaluation sample covers:

- customer refund batch
- internal treasury rebalance
- stablecoin bridge transfer
- payment settlement retry
- custody wallet-policy change
- tokenized collateral movement
- transaction-limit change
- reserve-status publication

The sample intentionally includes mixed outcomes:

- low-risk actions that should be able to proceed
- actions that should be constrained rather than blocked
- actions that should be blocked because recoverability is weak
- hard Ref-gate failures where scoring cannot rescue the action
- autonomy-budget pressure across a sequence of financial actions

## What To Replace

Replace `examples/smerc_f_customer_eval_actions.json` with 5 to 25 metadata-only actions from one financial workflow family.

Good first workflow families:

- refund operations
- payment retries
- treasury rebalancing
- stablecoin liquidity operations
- tokenized collateral operations
- wallet-policy administration
- financial reporting publication

Use only metadata such as:

- action description
- actor or agent role
- tool family
- financial action type
- current control outcome
- reversibility estimate
- containment strength
- rollback latency
- evidence validity
- anomaly pressure
- impact scope
- cancel reliability
- authorization confidence
- external side-effect flag
- sensitive-data flag
- Ref-gate status
- declared tool-plan capabilities

Do not include:

- secrets
- API keys
- access tokens
- passwords
- wallet keys
- private keys
- raw customer records
- raw regulated transaction payloads
- AML case data
- sanctions-screening data
- production logs
- live fund-movement instructions

## How To Read The Output

The report is useful if it helps reviewers identify:

- financial actions that existing controls might allow but SMERC-F would constrain
- actions where rollback latency or weak containment makes automation unsafe
- actions where missing attestation, least privilege, or object-shape evidence should hard-stop execution
- actions where a narrower scope, dry run, checkpoint, or human approval could change posture
- whether a 30-day shadow-mode pilot is justified

## Evidence Boundary

This package proves that the current SMERC customer-evaluation runner can process financial-action metadata through Ref-gate checks, SMERC recoverability scoring, SPARTa routing, Decision Lifecycle Ledger records, and autonomy-budget evaluation.

It does not prove production safety, legal compliance, AML compliance, sanctions screening, fraud detection, custody safety, settlement correctness, payment execution safety, customer demand, incident reduction, or readiness to enforce in a live financial environment.

## Recommended Next Step

If the output is useful, ask the financial-services reviewer to provide 10 to 25 metadata-only actions from one workflow family and label whether each SMERC-F posture is useful, too strict, too permissive, or operationally unclear.

Move to a shadow-mode pilot only if the reviewer can name an accountable workflow owner, define success metrics, and preserve the boundary that existing financial controls remain authoritative.
