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

## Run From GitHub Actions

Copy `integrations/github_actions/customer_evaluation_workflow.yml` into `.github/workflows/smerc-customer-evaluation.yml` in a review repository.

Then run the workflow manually with:

```text
action_file = examples/customer_eval_actions.json
```

For a real evaluation, replace the default path with a repository-local metadata-only input file that follows `smerc.customer-evaluation.v1`.

The workflow:

- checks out the repository
- sets up Python
- runs `python -m reference_engine.customer_evaluation`
- uploads `smerc-customer-evaluation` as a 14-day artifact

It does not require a remote SMERC API, secrets, production credentials, or write access to customer systems.

## Run From This Repository's Actions Tab

This repository also includes `.github/workflows/customer-evaluations.yml`.

Use it when a reviewer wants to see the public examples execute directly from the GitHub Actions tab.

Set `evaluation_set` to one of these manual options:

- `both` runs the general customer evaluation and the SMERC-F financial customer evaluation.
- `general` runs only `examples/customer_eval_actions.json`.
- `smerc-f` runs only `examples/smerc_f_customer_eval_actions.json`.

The workflow uploads one artifact named `smerc-customer-evaluations` containing generated markdown and JSON reports.

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
