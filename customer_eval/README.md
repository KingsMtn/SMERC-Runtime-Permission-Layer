# SMERC Self-Service Company Evaluation Kit

## Purpose

This folder is the commercial entry point for a company that wants to test SMERC without a live integration.

The evaluation answers one question:

> Does recoverability-aware runtime permissioning change how our team reviews high-impact automated actions?

Use this kit for a metadata-only review of AI-agent actions, MCP tool calls, GitHub Actions, cloud automation, or financial runtime workflows.

For the shortest company-facing guide, start with `docs/Company_Reviewer_Front_Door.md`.

## Fastest Path

1. Open `examples/customer_metadata_template.json`.
2. Replace the sample actions with 5 to 25 metadata-only actions from one workflow family.
3. Do not include secrets, credentials, raw customer records, source code, wallet keys, production logs, private prompts, or regulated transaction payloads.
4. Run the evaluation locally:

```bash
python -m reference_engine.customer_evaluation examples/customer_metadata_template.json \
  --json-output reports/company_test/customer_evaluation_report.json \
  --markdown-output reports/company_test/Customer_Evaluation_Report.md \
  --pretty
```

5. Or run the public GitHub Actions workflow:

```text
https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/actions/workflows/customer-evaluations.yml
```

6. Review the generated report with a workflow owner, security reviewer, and platform or AI governance reviewer.

## What A Company Provides

Use one workflow family. Good first candidates:

- AI-assisted pull request or deployment workflow
- MCP tool-call workflow
- cloud administration workflow
- security response workflow
- support automation workflow
- financial operations workflow

For each action, provide metadata only:

- action description
- actor or agent role
- tool name
- action type
- risk scores from `0.0` to `1.0`
- side-effect level
- sensitive-data indicator
- rollback, containment, cancellation, dry-run, and approval availability
- typed contract, attestation, least privilege, and expected object-shape results
- approximate requested scope units

## What SMERC Returns

The generated report includes:

- hard admission / Ref-gate result
- recoverability posture: `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE`
- irreversible exposure score
- reversible capacity score
- risk-adjusted authorization score
- execution route and controls
- Decision Lifecycle Ledger evidence
- autonomy-budget impact
- highest-exposure action list
- pilot-fit recommendation

## Available Evaluation Packs

| Path | Use |
| --- | --- |
| `examples/customer_metadata_template.json` | Starting template for a company-owned metadata-only test. |
| `examples/customer_eval_actions.json` | General AI-agent and automation examples. |
| `examples/cloud_admin_customer_eval_actions.json` | Cloud IAM, network, Kubernetes, DNS, database, and backup actions. |
| `examples/smerc_f_customer_eval_actions.json` | Financial runtime actions for refund, payment, treasury, stablecoin, tokenized collateral, and limit-change review. |
| `docs/Company_Reviewer_Front_Door.md` | Shortest route for a company reviewer choosing general, cloud-admin, financial runtime, or complete lifecycle proof. |
| `docs/Company_Test_Package.md` | Plain-English company test guide. |
| `docs/Run_Customer_Evaluation_From_GitHub.md` | Click-by-click GitHub Actions path. |
| `docs/Customer_Evaluation.md` | Technical evaluation guide. |
| `integrations/github_actions/customer_evaluation_workflow.yml` | Copyable workflow for a customer repository. |

## Pass Criteria

Treat the evaluation as useful only if reviewers identify at least one of these:

- a recoverability issue current allow/deny controls do not expose
- a constrained path that is better than simply allowing or blocking
- a hard-evidence failure that should stop scoring from supporting execution
- a high-impact action where rollback latency, containment, or cancellation materially changes judgment
- a workflow owner willing to test shadow-mode scoring against real workflow metadata

## Fail Criteria

Do not propose a pilot if:

- reviewers see no useful difference from existing IAM, OPA, CI/CD approval, ticketing, SIEM, or GRC controls
- the workflow cannot be described without sensitive data
- no workflow owner or reviewer group exists
- latency, workflow friction, or review burden would outweigh the expected value
- the prospect wants production enforcement before observe-mode evidence exists

## Evidence Boundary

This kit proves only that SMERC can process supplied metadata and generate a coherent review artifact. It does not prove production safety, regulatory compliance, incident reduction, customer demand, or enforce-mode readiness.
