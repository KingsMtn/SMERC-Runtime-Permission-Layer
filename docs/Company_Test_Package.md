# SMERC Company Test Package

## Purpose

This package is for a real company that wants to test SMERC without giving SMERC production access, secrets, customer data, source code, or regulated transaction payloads.

The test answers one question:

> Would recoverability-aware runtime permissioning change how our team reviews high-impact automated actions?

## Fastest Path

1. Open `examples/customer_metadata_template.json`.
2. Replace the sample organization, workflow, actors, tools, descriptions, and scores with 5 to 25 metadata-only actions from one workflow family.
3. Do not include secrets, credentials, raw customer records, source code, production logs, wallet keys, or regulated transaction payloads.
4. Run the file locally:

```bash
python -m reference_engine.customer_evaluation examples/customer_metadata_template.json \
  --json-output reports/company_test/customer_evaluation_report.json \
  --markdown-output reports/company_test/Customer_Evaluation_Report.md \
  --pretty
```

5. Or run the public workflow from GitHub Actions and select `company-template`:
   `https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/actions/workflows/customer-evaluations.yml`
6. Review the generated report with the workflow owner, security reviewer, and platform or AI governance reviewer.

## What To Provide

Use one workflow family. Good first candidates:

- AI-assisted pull request or deployment workflow
- MCP tool-call workflow
- cloud administration workflow
- support automation workflow
- security response workflow
- financial operations workflow

For each action, provide metadata only:

- action description
- actor or agent role
- tool name
- action type
- risk scores from `0.0` to `1.0`
- whether the action has external side effects
- whether sensitive data is involved
- whether rollback, containment, cancellation, dry run, and human approval are available
- whether typed contract, attestation, least privilege, and object shape checks pass
- approximate scope units

## How To Choose Scores

Use reviewer judgment for the first pass. SMERC does not need exact mathematical truth to start. It needs consistent relative scoring.

| Field | Low Means | High Means |
| --- | --- | --- |
| `base_action_risk` | routine action | inherently dangerous action |
| `reversibility` | hard to undo | easy to undo |
| `containment_strength` | broad blast radius | narrow blast radius |
| `rollback_latency` | quick rollback | slow rollback |
| `evidence_validity` | weak or missing evidence | strong trusted evidence |
| `anomaly_pressure` | normal context | unusual or unstable context |
| `impact_scope` | small impact | broad impact |
| `cancel_reliability` | hard to stop once started | reliable cancellation |
| `authorization_confidence` | unclear authority | clear authority |

## What A Useful Result Looks Like

A useful evaluation usually includes:

- at least one action that SMERC allows
- at least one action that SMERC constrains instead of blocking outright
- at least one action that SMERC blocks, freezes, or escalates
- at least one action where missing hard evidence changes the outcome
- a report that creates disagreement or discussion among reviewers

If every action is obviously safe or obviously forbidden, SMERC may not add much value for that workflow.

## Reviewer Questions

Ask these questions after reading the report:

- Which SMERC posture matched our reviewer judgment?
- Which posture was too strict?
- Which posture was too permissive?
- Which constrained action would we normally have blocked?
- Which allowed action should have been constrained?
- Which blocked action failed because of missing evidence rather than risk score?
- Would this report help us run a 30-day shadow-mode pilot?

## Pass/Fail Criteria

Treat the company test as successful only if reviewers can identify at least one of these:

- a recoverability issue their current allow/deny process does not expose
- a useful constrained path between allow and block
- a missing-evidence case that should fail before execution
- a high-impact action where rollback latency or containment changes the decision
- a workflow owner willing to run a bounded shadow-mode pilot

Treat the company test as unsuccessful if:

- reviewers see no difference from existing controls
- all useful decisions already come from IAM, policy-as-code, CI/CD approval, or ticket workflows
- the team cannot provide metadata without sensitive data
- no one owns the workflow or reviewer labels
- latency, workflow friction, or review burden would outweigh any benefit

## Evidence Boundary

This test proves only that SMERC can process supplied metadata and generate a coherent review artifact. It does not prove incident reduction, production safety, regulatory compliance, customer demand, or enforce-mode readiness.

## Next Step

If the company test creates useful reviewer disagreement or identifies recoverability gaps, move to one 30-day shadow-mode pilot. Keep existing systems authoritative. Use SMERC only to score, report, and compare outcomes until customer evidence supports a stronger mode.
