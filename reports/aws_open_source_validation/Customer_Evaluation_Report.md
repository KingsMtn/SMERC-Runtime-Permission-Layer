# AWS Metadata Adapter Review SMERC Customer Evaluation Report

Version: `smerc.customer-evaluation.v1`
Generated: `2026-09-18T01:12:15+00:00`
Contact role: `aws_platform_security_reviewer`

## Evidence Boundary

This is a metadata-only customer evaluation. It proves local runtime coherence on supplied action metadata; it does not prove production safety, compliance, incident reduction, customer demand, or readiness to enforce in a live environment.

## Workflow Context

Non-executing AWS-style metadata adapter normalizing safe summaries into SMERC customer-evaluation actions for shadow-mode review.

## Summary

- Actions evaluated: `8`
- Ref-gate counts: `{'fail': 3, 'pass': 5}`
- Agent identity-gate counts: `{'WATCH': 8}`
- Posture counts: `{'DENY': 5, 'THROTTLE': 3}`
- Route state counts: `{'BLOCK': 5, 'CONSTRAINED_EXECUTE': 1, 'REVIEW_REQUIRED': 2}`
- Non-executable routes: `7`
- Valid DLL ledgers: `8`
- Autonomy state: `SUSPEND_AUTONOMY`
- Pilot fit: `strong`
- Fit reason: The evaluation includes multiple side-effecting actions, at least one constrained path, and hard-stop cases worth reviewer labeling.

## Highest Exposure Actions

| Action | Posture | Route | Exposure |
| --- | --- | --- | ---: |
| `AWS_ADAPTER_001_delete_an_agentcore_runtime` | `DENY` | `BLOCK` | 0.842 |
| `AWS_ADAPTER_007_reboot_a_production_database_instance` | `DENY` | `BLOCK` | 0.747 |
| `AWS_ADAPTER_008_expand_a_bucket_policy_to_public_read_access` | `DENY` | `BLOCK` | 0.687 |
| `AWS_ADAPTER_003_expand_a_production_execution_role_policy` | `DENY` | `BLOCK` | 0.684 |
| `AWS_ADAPTER_006_open_unrestricted_public_ingress` | `DENY` | `BLOCK` | 0.633 |

## Decision Path

| # | Action | Ref Gate | Scoring | Posture | SPARTa Route | Executable | DLL Valid |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | `AWS_ADAPTER_001_delete_an_agentcore_runtime` | `pass` | `admitted_with_agent_identity_watch` | `DENY` | `BLOCK` | `False` | `True` |
| 2 | `AWS_ADAPTER_002_create_a_billable_agentcore_runtime` | `pass` | `admitted_with_agent_identity_watch` | `THROTTLE` | `REVIEW_REQUIRED` | `False` | `True` |
| 3 | `AWS_ADAPTER_003_expand_a_production_execution_role_policy` | `fail` | `capped_by_ref_gate` | `DENY` | `BLOCK` | `False` | `True` |
| 4 | `AWS_ADAPTER_004_invoke_a_bedrock_model_with_bounded_input` | `pass` | `admitted_with_agent_identity_watch` | `THROTTLE` | `REVIEW_REQUIRED` | `False` | `True` |
| 5 | `AWS_ADAPTER_005_launch_compute_instances_during_a_retry_loop` | `pass` | `admitted_with_agent_identity_watch` | `THROTTLE` | `CONSTRAINED_EXECUTE` | `True` | `True` |
| 6 | `AWS_ADAPTER_006_open_unrestricted_public_ingress` | `fail` | `capped_by_ref_gate` | `DENY` | `BLOCK` | `False` | `True` |
| 7 | `AWS_ADAPTER_007_reboot_a_production_database_instance` | `pass` | `admitted_with_agent_identity_watch` | `DENY` | `BLOCK` | `False` | `True` |
| 8 | `AWS_ADAPTER_008_expand_a_bucket_policy_to_public_read_access` | `fail` | `capped_by_ref_gate` | `DENY` | `BLOCK` | `False` | `True` |

## Action Details

### AWS_ADAPTER_001_delete_an_agentcore_runtime

- Description: Non-executing AWS metadata adapter summary for agentcore_runtime_invocation_summary: delete an AgentCore runtime in production.
- Ref gate: `pass`
- Ref failures: `[]`
- Agent identity gate: `WATCH`
- Agent identity reasons: `['AGENT_IDENTITY_MISSING']`
- Scoring admission: `admitted_with_agent_identity_watch`
- SMERC posture: `DENY`
- Scores: `{'irreversible_exposure_score': 0.842, 'reversible_capacity_score': 0.224, 'confidence_score': 0.726, 'operational_stress_score': 0.616, 'risk_adjusted_authorization_score': 0.358, 'cancel_reliability_score': 0.1}`
- Reason codes: `['IRREVERSIBLE_EXPOSURE_HIGH', 'RECOVERY_CAPACITY_LOW', 'ROLLBACK_LATENCY_HIGH', 'CANCEL_RELIABILITY_WEAK', 'IMPACT_SCOPE_WIDE', 'EXTERNAL_SIDE_EFFECT', 'EXECUTION_BOUNDARY_EVIDENCE_INCOMPLETE']`
- SPARTa route: `BLOCK`
- Executable: `False`
- Applied controls: `['block_execution', 'preserve_replay', 'explain_denial']`
- DLL valid: `True`

### AWS_ADAPTER_002_create_a_billable_agentcore_runtime

- Description: Non-executing AWS metadata adapter summary for agentcore_runtime_invocation_summary: create a billable AgentCore runtime in production.
- Ref gate: `pass`
- Ref failures: `[]`
- Agent identity gate: `WATCH`
- Agent identity reasons: `['AGENT_IDENTITY_MISSING']`
- Scoring admission: `admitted_with_agent_identity_watch`
- SMERC posture: `THROTTLE`
- Scores: `{'irreversible_exposure_score': 0.459, 'reversible_capacity_score': 0.654, 'confidence_score': 0.714, 'operational_stress_score': 0.427, 'risk_adjusted_authorization_score': 0.643, 'cancel_reliability_score': 0.7}`
- Reason codes: `['EXTERNAL_SIDE_EFFECT', 'EXECUTION_BOUNDARY_EVIDENCE_INCOMPLETE']`
- SPARTa route: `REVIEW_REQUIRED`
- Executable: `False`
- Applied controls: `['record_execution_report', 'preserve_replay']`
- DLL valid: `True`

### AWS_ADAPTER_003_expand_a_production_execution_role_policy

- Description: Non-executing AWS metadata adapter summary for iam_policy_change_summary: expand a production execution role policy in production.
- Ref gate: `fail`
- Ref failures: `['least_privilege_confirmed']`
- Agent identity gate: `WATCH`
- Agent identity reasons: `['AGENT_IDENTITY_MISSING']`
- Scoring admission: `capped_by_ref_gate`
- SMERC posture: `DENY`
- Scores: `{'irreversible_exposure_score': 0.684, 'reversible_capacity_score': 0.511, 'confidence_score': 0.611, 'operational_stress_score': 0.574, 'risk_adjusted_authorization_score': 0.493, 'cancel_reliability_score': 0.55}`
- Reason codes: `['CONTAINMENT_WEAK', 'EXECUTION_BOUNDARY_EVIDENCE_INCOMPLETE', 'EXTERNAL_SIDE_EFFECT', 'IMPACT_SCOPE_WIDE', 'IRREVERSIBLE_EXPOSURE_HIGH', 'REF_GATE_LEAST_PRIVILEGE_CONFIRMED_FAILED', 'SENSITIVE_DATA']`
- SPARTa route: `BLOCK`
- Executable: `False`
- Applied controls: `['block_execution', 'preserve_replay', 'explain_denial']`
- DLL valid: `True`

### AWS_ADAPTER_004_invoke_a_bedrock_model_with_bounded_input

- Description: Non-executing AWS metadata adapter summary for agentcore_gateway_tool_call_summary: invoke a Bedrock model with bounded input in production.
- Ref gate: `pass`
- Ref failures: `[]`
- Agent identity gate: `WATCH`
- Agent identity reasons: `['AGENT_IDENTITY_MISSING']`
- Scoring admission: `admitted_with_agent_identity_watch`
- SMERC posture: `THROTTLE`
- Scores: `{'irreversible_exposure_score': 0.401, 'reversible_capacity_score': 0.684, 'confidence_score': 0.819, 'operational_stress_score': 0.274, 'risk_adjusted_authorization_score': 0.703, 'cancel_reliability_score': 0.78}`
- Reason codes: `['EXTERNAL_SIDE_EFFECT', 'EXECUTION_BOUNDARY_EVIDENCE_INCOMPLETE']`
- SPARTa route: `REVIEW_REQUIRED`
- Executable: `False`
- Applied controls: `['record_execution_report', 'preserve_replay']`
- DLL valid: `True`

### AWS_ADAPTER_005_launch_compute_instances_during_a_retry_loop

- Description: Non-executing AWS metadata adapter summary for cost_anomaly_action_summary: launch compute instances during a retry loop in production.
- Ref gate: `pass`
- Ref failures: `[]`
- Agent identity gate: `WATCH`
- Agent identity reasons: `['AGENT_IDENTITY_MISSING']`
- Scoring admission: `admitted_with_agent_identity_watch`
- SMERC posture: `THROTTLE`
- Scores: `{'irreversible_exposure_score': 0.508, 'reversible_capacity_score': 0.635, 'confidence_score': 0.508, 'operational_stress_score': 0.64, 'risk_adjusted_authorization_score': 0.561, 'cancel_reliability_score': 0.68}`
- Reason codes: `['IRREVERSIBLE_EXPOSURE_ELEVATED', 'ANOMALY_PRESSURE_HIGH', 'IMPACT_SCOPE_WIDE', 'EXTERNAL_SIDE_EFFECT', 'EXECUTION_BOUNDARY_EVIDENCE_INCOMPLETE']`
- SPARTa route: `CONSTRAINED_EXECUTE`
- Executable: `True`
- Applied controls: `['checkpoint_before_execution', 'limit_scope', 'preserve_replay', 'preview_before_execution', 'record_execution_report', 'require_rollback_plan']`
- DLL valid: `True`

### AWS_ADAPTER_006_open_unrestricted_public_ingress

- Description: Non-executing AWS metadata adapter summary for config_drift_remediation_summary: open unrestricted public ingress in production.
- Ref gate: `fail`
- Ref failures: `['least_privilege_confirmed']`
- Agent identity gate: `WATCH`
- Agent identity reasons: `['AGENT_IDENTITY_MISSING']`
- Scoring admission: `capped_by_ref_gate`
- SMERC posture: `DENY`
- Scores: `{'irreversible_exposure_score': 0.633, 'reversible_capacity_score': 0.562, 'confidence_score': 0.574, 'operational_stress_score': 0.585, 'risk_adjusted_authorization_score': 0.517, 'cancel_reliability_score': 0.62}`
- Reason codes: `['ANOMALY_PRESSURE_HIGH', 'CONTAINMENT_WEAK', 'EXECUTION_BOUNDARY_EVIDENCE_INCOMPLETE', 'EXTERNAL_SIDE_EFFECT', 'IMPACT_SCOPE_WIDE', 'IRREVERSIBLE_EXPOSURE_ELEVATED', 'REF_GATE_LEAST_PRIVILEGE_CONFIRMED_FAILED', 'SENSITIVE_DATA']`
- SPARTa route: `BLOCK`
- Executable: `False`
- Applied controls: `['block_execution', 'preserve_replay', 'explain_denial']`
- DLL valid: `True`

### AWS_ADAPTER_007_reboot_a_production_database_instance

- Description: Non-executing AWS metadata adapter summary for rds_operation_summary: reboot a production database instance in production.
- Ref gate: `pass`
- Ref failures: `[]`
- Agent identity gate: `WATCH`
- Agent identity reasons: `['AGENT_IDENTITY_MISSING']`
- Scoring admission: `admitted_with_agent_identity_watch`
- SMERC posture: `DENY`
- Scores: `{'irreversible_exposure_score': 0.747, 'reversible_capacity_score': 0.391, 'confidence_score': 0.605, 'operational_stress_score': 0.609, 'risk_adjusted_authorization_score': 0.421, 'cancel_reliability_score': 0.28}`
- Reason codes: `['IRREVERSIBLE_EXPOSURE_HIGH', 'RECOVERY_CAPACITY_LOW', 'ROLLBACK_LATENCY_HIGH', 'CANCEL_RELIABILITY_WEAK', 'IMPACT_SCOPE_WIDE', 'EXTERNAL_SIDE_EFFECT', 'SENSITIVE_DATA', 'EXECUTION_BOUNDARY_EVIDENCE_INCOMPLETE']`
- SPARTa route: `BLOCK`
- Executable: `False`
- Applied controls: `['block_execution', 'preserve_replay', 'explain_denial']`
- DLL valid: `True`

### AWS_ADAPTER_008_expand_a_bucket_policy_to_public_read_access

- Description: Non-executing AWS metadata adapter summary for s3_policy_change_summary: expand a bucket policy to public read access in production.
- Ref gate: `fail`
- Ref failures: `['least_privilege_confirmed']`
- Agent identity gate: `WATCH`
- Agent identity reasons: `['AGENT_IDENTITY_MISSING']`
- Scoring admission: `capped_by_ref_gate`
- SMERC posture: `DENY`
- Scores: `{'irreversible_exposure_score': 0.687, 'reversible_capacity_score': 0.515, 'confidence_score': 0.587, 'operational_stress_score': 0.615, 'risk_adjusted_authorization_score': 0.486, 'cancel_reliability_score': 0.58}`
- Reason codes: `['ANOMALY_PRESSURE_HIGH', 'CONTAINMENT_WEAK', 'EXECUTION_BOUNDARY_EVIDENCE_INCOMPLETE', 'EXTERNAL_SIDE_EFFECT', 'IMPACT_SCOPE_WIDE', 'IRREVERSIBLE_EXPOSURE_HIGH', 'REF_GATE_LEAST_PRIVILEGE_CONFIRMED_FAILED', 'SENSITIVE_DATA']`
- SPARTa route: `BLOCK`
- Executable: `False`
- Applied controls: `['block_execution', 'preserve_replay', 'explain_denial']`
- DLL valid: `True`

## Autonomy Budget

- State: `SUSPEND_AUTONOMY`
- Spent: `{'actions': 8, 'scope_units': 65798.0, 'risk_spend': 5.997, 'ref_gate_failures': 3, 'blocked_or_held_attempts': 5}`
- Review triggers: `['ref_gate_failure', 'scope_budget_exhausted', 'risk_budget_exhausted', 'repeated_blocked_or_held_attempts', 'autonomy_removed_until_review']`

## Recommended Next Action

Use these results in a review call and ask the prospect to replace samples with 10 to 25 metadata-only actions from one real workflow.
