# SMERC Customer Evaluation

## Purpose

This is the self-service path for a security, platform, or AI governance reviewer who wants to test SMERC against their own workflow metadata before discussing a pilot.

It answers one practical question:

> If I give SMERC metadata-only examples of proposed AI-agent or automation actions, can it produce a complete runtime evaluation package without touching production systems?

## Run

From the repository root:

```bash
python -m reference_engine.customer_evaluation examples/customer_eval_actions.json --pretty
```

Generated files:

```text
reports/customer_evaluation/customer_evaluation_report.json
reports/customer_evaluation/Customer_Evaluation_Report.md
```

## What The Evaluation Includes

- metadata-only input validation
- sensitive-key rejection for secrets, tokens, credentials, wallet keys, raw customer records, source code, and production logs
- Ref-gate checks for typed contract validity, attestation validity, least privilege, and expected object shape
- SMERC recoverability posture
- SPARTa route behavior
- Decision Lifecycle Ledger evidence
- autonomy budget impact
- pilot-fit recommendation

## What To Replace

Start with `examples/customer_eval_actions.json`, then replace the sample actions with 5 to 25 metadata-only examples from one real workflow.

Use only metadata such as:

- action description
- actor or agent role
- tool name
- action type
- risk scores from 0.0 to 1.0
- whether the action has external side effects
- whether sensitive data is involved
- whether rollback, containment, and cancellation are available
- whether the tool contract, attestation, least privilege, and object shape passed
- declared SPARTa tool-plan capabilities

Do not include:

- secrets
- API keys
- access tokens
- passwords
- wallet keys
- source code
- raw customer records
- raw regulated transaction payloads
- production logs

## How To Read The Report

The report is useful if it shows:

- at least one action that can proceed normally
- at least one action constrained rather than blocked
- at least one action blocked, frozen, or escalated because recovery is weak
- at least one hard Ref-gate failure where scoring cannot rescue the action
- valid Decision Lifecycle Ledger records
- a clear autonomy-budget state after the evaluated action stream

## Evidence Boundary

This customer evaluation proves local runtime coherence on supplied metadata. It does not prove production safety, compliance, incident reduction, customer demand, financial control effectiveness, prompt-injection defense, or readiness to enforce in a live environment.

## Next Step

If the evaluation is strong, ask the organization to provide 10 to 25 metadata-only actions from one workflow and run a review session. Move to a shadow-mode pilot only if reviewers can label outcomes, define success metrics, and name an accountable workflow owner.
