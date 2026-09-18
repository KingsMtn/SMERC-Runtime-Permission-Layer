# AWS Metadata Adapter Review SMERC Customer Evaluation Report

Version: `smerc.customer-evaluation.v1`
Generated: `2026-09-18T00:41:46+00:00`
Contact role: `aws_platform_security_reviewer`

## Evidence Boundary

This is a metadata-only customer evaluation. It proves local runtime coherence on supplied action metadata; it does not prove production safety, compliance, incident reduction, customer demand, or readiness to enforce in a live environment.

## Workflow Context

Non-executing AWS-style metadata adapter normalizing safe summaries into SMERC customer-evaluation actions for shadow-mode review.

## Summary

- Actions evaluated: `5`
- Ref-gate counts: `{'fail': 3, 'pass': 2}`
- Agent identity-gate counts: `{'WATCH': 5}`
- Posture counts: `{'DENY': 3, 'THROTTLE': 2}`
- Route state counts: `{'BLOCK': 3, 'CONSTRAINED_EXECUTE': 2}`
- Non-executable routes: `3`
- Valid DLL ledgers: `5`
- Autonomy state: `SUSPEND_AUTONOMY`
- Pilot fit: `strong`
- Fit reason: The evaluation includes multiple side-effecting actions, at least one constrained path, and hard-stop cases worth reviewer labeling.

## Highest Exposure Actions

| Action | Posture | Route | Exposure |
| --- | --- | --- | ---: |
| `AWS_ADAPTER_002_expand_execution_role_permissions` | `DENY` | `BLOCK` | 0.748 |
| `AWS_ADAPTER_004_widen_bucket_policy_access` | `DENY` | `BLOCK` | 0.73 |
| `AWS_ADAPTER_003_execute_stateful_change_set` | `THROTTLE` | `CONSTRAINED_EXECUTE` | 0.645 |
| `AWS_ADAPTER_005_increase_compute_capacity_during_retry_loop` | `DENY` | `BLOCK` | 0.634 |
| `AWS_ADAPTER_001_invoke_action_group_update_config` | `THROTTLE` | `CONSTRAINED_EXECUTE` | 0.586 |

## Decision Path

| # | Action | Ref Gate | Scoring | Posture | SPARTa Route | Executable | DLL Valid |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | `AWS_ADAPTER_001_invoke_action_group_update_config` | `pass` | `admitted_with_agent_identity_watch` | `THROTTLE` | `CONSTRAINED_EXECUTE` | `True` | `True` |
| 2 | `AWS_ADAPTER_002_expand_execution_role_permissions` | `fail` | `capped_by_ref_gate` | `DENY` | `BLOCK` | `False` | `True` |
| 3 | `AWS_ADAPTER_003_execute_stateful_change_set` | `pass` | `admitted_with_agent_identity_watch` | `THROTTLE` | `CONSTRAINED_EXECUTE` | `True` | `True` |
| 4 | `AWS_ADAPTER_004_widen_bucket_policy_access` | `fail` | `capped_by_ref_gate` | `DENY` | `BLOCK` | `False` | `True` |
| 5 | `AWS_ADAPTER_005_increase_compute_capacity_during_retry_loop` | `fail` | `capped_by_ref_gate` | `DENY` | `BLOCK` | `False` | `True` |

## Action Details

### AWS_ADAPTER_001_invoke_action_group_update_config

- Description: Non-executing AWS metadata adapter summary for agentcore_gateway_tool_call_summary: invoke action group update config in production.
- Ref gate: `pass`
- Ref failures: `[]`
- Agent identity gate: `WATCH`
- Agent identity reasons: `['AGENT_IDENTITY_MISSING']`
- Scoring admission: `admitted_with_agent_identity_watch`
- SMERC posture: `THROTTLE`
- Scores: `{'irreversible_exposure_score': 0.586, 'reversible_capacity_score': 0.59, 'confidence_score': 0.697, 'operational_stress_score': 0.435, 'risk_adjusted_authorization_score': 0.578, 'cancel_reliability_score': 0.66}`
- Reason codes: `['IRREVERSIBLE_EXPOSURE_ELEVATED', 'EXTERNAL_SIDE_EFFECT', 'SENSITIVE_DATA', 'EXECUTION_BOUNDARY_EVIDENCE_INCOMPLETE']`
- SPARTa route: `CONSTRAINED_EXECUTE`
- Executable: `True`
- Applied controls: `['checkpoint_before_execution', 'limit_scope', 'preserve_replay', 'preview_before_execution', 'record_execution_report', 'require_rollback_plan']`
- DLL valid: `True`

### AWS_ADAPTER_002_expand_execution_role_permissions

- Description: Non-executing AWS metadata adapter summary for iam_policy_change_summary: expand execution role permissions in production.
- Ref gate: `fail`
- Ref failures: `['least_privilege_confirmed']`
- Agent identity gate: `WATCH`
- Agent identity reasons: `['AGENT_IDENTITY_MISSING']`
- Scoring admission: `capped_by_ref_gate`
- SMERC posture: `DENY`
- Scores: `{'irreversible_exposure_score': 0.748, 'reversible_capacity_score': 0.428, 'confidence_score': 0.577, 'operational_stress_score': 0.588, 'risk_adjusted_authorization_score': 0.429, 'cancel_reliability_score': 0.53}`
- Reason codes: `['CONTAINMENT_WEAK', 'EXECUTION_BOUNDARY_EVIDENCE_INCOMPLETE', 'EXTERNAL_SIDE_EFFECT', 'IMPACT_SCOPE_WIDE', 'IRREVERSIBLE_EXPOSURE_HIGH', 'REF_GATE_LEAST_PRIVILEGE_CONFIRMED_FAILED', 'SENSITIVE_DATA']`
- SPARTa route: `BLOCK`
- Executable: `False`
- Applied controls: `['block_execution', 'preserve_replay', 'explain_denial']`
- DLL valid: `True`

### AWS_ADAPTER_003_execute_stateful_change_set

- Description: Non-executing AWS metadata adapter summary for cloudformation_changeset_summary: execute stateful change set in production.
- Ref gate: `pass`
- Ref failures: `[]`
- Agent identity gate: `WATCH`
- Agent identity reasons: `['AGENT_IDENTITY_MISSING']`
- Scoring admission: `admitted_with_agent_identity_watch`
- SMERC posture: `THROTTLE`
- Scores: `{'irreversible_exposure_score': 0.645, 'reversible_capacity_score': 0.441, 'confidence_score': 0.64, 'operational_stress_score': 0.554, 'risk_adjusted_authorization_score': 0.479, 'cancel_reliability_score': 0.5}`
- Reason codes: `['IRREVERSIBLE_EXPOSURE_ELEVATED', 'IMPACT_SCOPE_WIDE', 'EXTERNAL_SIDE_EFFECT', 'EXECUTION_BOUNDARY_EVIDENCE_INCOMPLETE']`
- SPARTa route: `CONSTRAINED_EXECUTE`
- Executable: `True`
- Applied controls: `['checkpoint_before_execution', 'limit_scope', 'preserve_replay', 'preview_before_execution', 'record_execution_report']`
- DLL valid: `True`

### AWS_ADAPTER_004_widen_bucket_policy_access

- Description: Non-executing AWS metadata adapter summary for s3_policy_change_summary: widen bucket policy access in production.
- Ref gate: `fail`
- Ref failures: `['least_privilege_confirmed']`
- Agent identity gate: `WATCH`
- Agent identity reasons: `['AGENT_IDENTITY_MISSING']`
- Scoring admission: `capped_by_ref_gate`
- SMERC posture: `DENY`
- Scores: `{'irreversible_exposure_score': 0.73, 'reversible_capacity_score': 0.459, 'confidence_score': 0.494, 'operational_stress_score': 0.635, 'risk_adjusted_authorization_score': 0.422, 'cancel_reliability_score': 0.62}`
- Reason codes: `['ANOMALY_PRESSURE_HIGH', 'CONTAINMENT_WEAK', 'EXECUTION_BOUNDARY_EVIDENCE_INCOMPLETE', 'EXTERNAL_SIDE_EFFECT', 'IMPACT_SCOPE_WIDE', 'IRREVERSIBLE_EXPOSURE_HIGH', 'REF_GATE_LEAST_PRIVILEGE_CONFIRMED_FAILED', 'SENSITIVE_DATA']`
- SPARTa route: `BLOCK`
- Executable: `False`
- Applied controls: `['block_execution', 'preserve_replay', 'explain_denial']`
- DLL valid: `True`

### AWS_ADAPTER_005_increase_compute_capacity_during_retry_loop

- Description: Non-executing AWS metadata adapter summary for cost_anomaly_action_summary: increase compute capacity during retry loop in production.
- Ref gate: `fail`
- Ref failures: `['least_privilege_confirmed']`
- Agent identity gate: `WATCH`
- Agent identity reasons: `['AGENT_IDENTITY_MISSING']`
- Scoring admission: `capped_by_ref_gate`
- SMERC posture: `DENY`
- Scores: `{'irreversible_exposure_score': 0.634, 'reversible_capacity_score': 0.466, 'confidence_score': 0.449, 'operational_stress_score': 0.686, 'risk_adjusted_authorization_score': 0.436, 'cancel_reliability_score': 0.55}`
- Reason codes: `['ANOMALY_PRESSURE_HIGH', 'CONTAINMENT_WEAK', 'EVIDENCE_VALIDITY_LOW', 'EXECUTION_BOUNDARY_EVIDENCE_INCOMPLETE', 'EXTERNAL_SIDE_EFFECT', 'IMPACT_SCOPE_WIDE', 'IRREVERSIBLE_EXPOSURE_ELEVATED', 'REF_GATE_LEAST_PRIVILEGE_CONFIRMED_FAILED']`
- SPARTa route: `BLOCK`
- Executable: `False`
- Applied controls: `['block_execution', 'preserve_replay', 'explain_denial']`
- DLL valid: `True`

## Autonomy Budget

- State: `SUSPEND_AUTONOMY`
- Spent: `{'actions': 5, 'scope_units': 366.0, 'risk_spend': 4.733, 'ref_gate_failures': 3, 'blocked_or_held_attempts': 3}`
- Review triggers: `['ref_gate_failure', 'risk_budget_exhausted', 'repeated_blocked_or_held_attempts', 'autonomy_removed_until_review']`

## Recommended Next Action

Use these results in a review call and ask the prospect to replace samples with 10 to 25 metadata-only actions from one real workflow.
