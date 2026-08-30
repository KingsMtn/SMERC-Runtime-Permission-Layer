# Customer-Owned Metadata Request

Generated: `2026-08-30T15:27:08+00:00`
Version: `smerc.customer-owned-metadata-request.v1`
Workflow family: `general`
Requested actions: `10`

## Request

Please replace the public examples with 10 metadata-only actions from one general workflow family.

## Acceptable Action Types

- AI-assisted code or deployment action
- MCP tool call
- support automation action
- security-response automation action

## Required Metadata Fields

- `action_id`
- `action_description`
- `actor_or_agent_role`
- `tool_family`
- `environment`
- `requested_scope`
- `current_control_outcome`
- `base_action_risk`
- `reversibility`
- `containment_strength`
- `rollback_latency`
- `evidence_validity`
- `anomaly_pressure`
- `impact_scope`
- `cancel_reliability`
- `authorization_confidence`
- `typed_contract_present`
- `attestation_valid`
- `least_privilege_confirmed`
- `object_shape_valid`

## Do Not Provide

- secrets, API keys, tokens, passwords, private keys, or wallet keys
- source code bodies, private prompts, model prompts, or proprietary policies
- raw customer records, regulated transaction payloads, AML case files, or sanctions-screening records
- production logs, incident details, account numbers, or confidential infrastructure diagrams
- live credentials or authorization to execute production actions

## Commands

```bash
python -m reference_engine.customer_evaluation customer_working/customer_actions.json --json-output reports/customer_working/customer_evaluation_report.json --markdown-output reports/customer_working/Customer_Evaluation_Report.md --pretty

python -m reference_engine.customer_metadata_validator --checklist customer_working/customer_metadata_substitution_checklist.json --prospect-route customer_working/prospect_route.json --customer-intake customer_working/customer_action_intake.json --pilot-handoff customer_working/pilot_handoff.json --pretty

python -m reference_engine.serious_report_performance --iterations 5 --pretty
```

## Reviewer Questions

- Which SMERC posture matched current reviewer judgment?
- Which action was usefully constrained instead of simply allowed or blocked?
- Which action failed because evidence was missing or untrusted?
- Which p95 workflow overhead would make this unsuitable?
- Would these results justify a bounded shadow-mode pilot?

## Work / Result / Impact

- Work: Ask an external reviewer to supply safe metadata-only actions from one real workflow.
- Result: SMERC can compare customer-owned action metadata against its public examples, posture logic, SPARTa routes, postcondition evidence expectations, and local performance metrics.
- Impact: The project can move from synthetic proof toward reviewer-owned evidence without requesting secrets, production access, regulated payloads, or enforcement authority.

## Evidence Boundary

Customer-owned metadata review is still pre-production and shadow-mode. It does not prove customer demand, incident reduction, compliance, production safety, or enforce-mode readiness.
