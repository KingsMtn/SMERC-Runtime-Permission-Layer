# 20-Minute SMERC Company Evaluation

## Who This Is For

Use this path when a security, platform, DevSecOps, or AI governance team wants to inspect SMERC quickly without installing a service or sharing sensitive data.

## Minute 0-3: Pick One Workflow

Choose one workflow where automation can create real side effects:

- AI-assisted production deployment
- MCP tool call with write access
- cloud IAM or network change
- support automation that modifies customer state
- security automation that quarantines or revokes access
- financial workflow that changes refund, transfer, payment, limit, liquidity, or collateral state

Do not mix unrelated workflows in the first evaluation.

## Minute 3-8: Prepare Metadata

Copy `examples/customer_metadata_template.json`.

Replace the sample actions with 5 to 25 action records from the selected workflow. Use approximate reviewer scores where exact measurements are unavailable.

Required score fields:

| Field | Meaning |
| --- | --- |
| `base_action_risk` | Inherent action danger before controls. |
| `reversibility` | How easily the action can be undone. |
| `containment_strength` | How narrow the blast radius is. |
| `rollback_latency` | How slow rollback or repair would be. |
| `evidence_validity` | How trustworthy the decision evidence is. |
| `anomaly_pressure` | How unusual, unstable, or suspicious the context is. |
| `impact_scope` | How broad the affected system, user, financial, or operational scope is. |
| `cancel_reliability` | Whether the action can be stopped after launch. |
| `authorization_confidence` | Whether the actor clearly has authority for this action. |

## Minute 8-12: Run The Evaluation

Local command:

```bash
python -m reference_engine.customer_evaluation examples/customer_metadata_template.json \
  --json-output reports/company_test/customer_evaluation_report.json \
  --markdown-output reports/company_test/Customer_Evaluation_Report.md \
  --pretty
```

GitHub-only path:

1. Open `Actions`.
2. Open `Runtime Customer Evaluations`.
3. Select `Run workflow`.
4. Select `company-template` or a custom branch containing the company metadata file.
5. Download the `smerc-customer-evaluations` artifact.

## Minute 12-18: Review The Report

Look for:

- actions where SMERC constrains rather than blocks
- actions where hard evidence fails before recoverability can support execution
- actions where rollback latency or containment changes the posture
- actions where broad impact scope forces review
- action streams that consume too much autonomy budget

Ask the reviewers:

- Which posture matched our existing judgment?
- Which posture was too strict?
- Which posture was too permissive?
- Which constrained route would keep useful automation moving?
- Which allowed action should have required more evidence?
- Which denied or frozen action reveals a recovery gap?

## Minute 18-20: Decide The Next Step

Move to a 30-day observe-mode pilot only if:

- one workflow owner wants to continue
- reviewers can label outcomes weekly
- existing controls remain authoritative
- SMERC can run without production secrets or sensitive payloads
- the team wants to measure reviewer agreement, override rates, false release candidates, useful constraints, unavailable evaluations, and latency overhead

If those conditions are not met, stay at review-only status.

