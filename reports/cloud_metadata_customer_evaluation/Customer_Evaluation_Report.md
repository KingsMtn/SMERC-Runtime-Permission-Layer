# Cloud Metadata Review SMERC Customer Evaluation Report

Version: `smerc.customer-evaluation.v1`
Generated: `2026-08-30T00:52:18+00:00`
Contact role: `cloud_platform_reviewer`

## Evidence Boundary

This is a metadata-only customer evaluation. It proves local runtime coherence on supplied action metadata; it does not prove production safety, compliance, incident reduction, customer demand, or readiness to enforce in a live environment.

## Workflow Context

Read-only cloud change metadata normalized into SMERC customer-evaluation actions for IAM, network, database, Kubernetes, DNS, and backup-policy review.

## Summary

- Actions evaluated: `6`
- Ref-gate counts: `{'fail': 3, 'pass': 3}`
- Agent identity-gate counts: `{'WATCH': 6}`
- Posture counts: `{'DENY': 3, 'THROTTLE': 3}`
- Route state counts: `{'BLOCK': 3, 'CONSTRAINED_EXECUTE': 3}`
- Non-executable routes: `3`
- Valid DLL ledgers: `6`
- Autonomy state: `SUSPEND_AUTONOMY`
- Pilot fit: `strong`
- Fit reason: The evaluation includes multiple side-effecting actions, at least one constrained path, and hard-stop cases worth reviewer labeling.

## Highest Exposure Actions

| Action | Posture | Route | Exposure |
| --- | --- | --- | ---: |
| `CLOUD_EXPORT_003_delete_idle_database_cluster` | `DENY` | `BLOCK` | 0.964 |
| `CLOUD_EXPORT_006_shorten_backup_retention_after_cost_anomaly` | `DENY` | `BLOCK` | 0.827 |
| `CLOUD_EXPORT_001_expand_production_role_policy` | `DENY` | `BLOCK` | 0.763 |
| `CLOUD_EXPORT_002_widen_database_network_access` | `THROTTLE` | `CONSTRAINED_EXECUTE` | 0.705 |
| `CLOUD_EXPORT_005_cutover_production_dns_endpoint` | `THROTTLE` | `CONSTRAINED_EXECUTE` | 0.613 |

## Decision Path

| # | Action | Ref Gate | Scoring | Posture | SPARTa Route | Executable | DLL Valid |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | `CLOUD_EXPORT_001_expand_production_role_policy` | `fail` | `capped_by_ref_gate` | `DENY` | `BLOCK` | `False` | `True` |
| 2 | `CLOUD_EXPORT_002_widen_database_network_access` | `pass` | `admitted_with_agent_identity_watch` | `THROTTLE` | `CONSTRAINED_EXECUTE` | `True` | `True` |
| 3 | `CLOUD_EXPORT_003_delete_idle_database_cluster` | `fail` | `capped_by_ref_gate` | `DENY` | `BLOCK` | `False` | `True` |
| 4 | `CLOUD_EXPORT_004_rollout_canary_under_error_budget_pressure` | `pass` | `admitted_with_agent_identity_watch` | `THROTTLE` | `CONSTRAINED_EXECUTE` | `True` | `True` |
| 5 | `CLOUD_EXPORT_005_cutover_production_dns_endpoint` | `pass` | `admitted_with_agent_identity_watch` | `THROTTLE` | `CONSTRAINED_EXECUTE` | `True` | `True` |
| 6 | `CLOUD_EXPORT_006_shorten_backup_retention_after_cost_anomaly` | `fail` | `capped_by_ref_gate` | `DENY` | `BLOCK` | `False` | `True` |

## Action Details

### CLOUD_EXPORT_001_expand_production_role_policy

- Description: Read-only iam_access_analyzer_finding export proposes iam_policy_expansion in production for identity_access.
- Ref gate: `fail`
- Ref failures: `['least_privilege_confirmed']`
- Agent identity gate: `WATCH`
- Agent identity reasons: `['AGENT_IDENTITY_MISSING']`
- Scoring admission: `capped_by_ref_gate`
- SMERC posture: `DENY`
- Scores: `{'irreversible_exposure_score': 0.763, 'reversible_capacity_score': 0.426, 'confidence_score': 0.575, 'operational_stress_score': 0.607, 'risk_adjusted_authorization_score': 0.423, 'cancel_reliability_score': 0.52}`
- Reason codes: `['CONTAINMENT_WEAK', 'EXTERNAL_SIDE_EFFECT', 'IMPACT_SCOPE_WIDE', 'IRREVERSIBLE_EXPOSURE_HIGH', 'REF_GATE_LEAST_PRIVILEGE_CONFIRMED_FAILED', 'SENSITIVE_DATA']`
- SPARTa route: `BLOCK`
- Executable: `False`
- Applied controls: `['block_execution', 'preserve_replay', 'explain_denial']`
- DLL valid: `True`

### CLOUD_EXPORT_002_widen_database_network_access

- Description: Read-only terraform_plan_change export proposes security_group_change in production for network_boundary.
- Ref gate: `pass`
- Ref failures: `[]`
- Agent identity gate: `WATCH`
- Agent identity reasons: `['AGENT_IDENTITY_MISSING']`
- Scoring admission: `admitted_with_agent_identity_watch`
- SMERC posture: `THROTTLE`
- Scores: `{'irreversible_exposure_score': 0.705, 'reversible_capacity_score': 0.498, 'confidence_score': 0.534, 'operational_stress_score': 0.604, 'risk_adjusted_authorization_score': 0.458, 'cancel_reliability_score': 0.68}`
- Reason codes: `['IRREVERSIBLE_EXPOSURE_HIGH', 'CONTAINMENT_WEAK', 'IMPACT_SCOPE_WIDE', 'EXTERNAL_SIDE_EFFECT', 'SENSITIVE_DATA']`
- SPARTa route: `CONSTRAINED_EXECUTE`
- Executable: `True`
- Applied controls: `['checkpoint_before_execution', 'limit_scope', 'preserve_replay', 'preview_before_execution', 'record_execution_report', 'require_rollback_plan']`
- DLL valid: `True`

### CLOUD_EXPORT_003_delete_idle_database_cluster

- Description: Read-only cloudtrail_event_summary export proposes database_cluster_delete in production for data_plane.
- Ref gate: `fail`
- Ref failures: `['attestation_valid', 'object_shape_expected']`
- Agent identity gate: `WATCH`
- Agent identity reasons: `['AGENT_IDENTITY_MISSING']`
- Scoring admission: `capped_by_ref_gate`
- SMERC posture: `DENY`
- Scores: `{'irreversible_exposure_score': 0.964, 'reversible_capacity_score': 0.203, 'confidence_score': 0.438, 'operational_stress_score': 0.788, 'risk_adjusted_authorization_score': 0.232, 'cancel_reliability_score': 0.24}`
- Reason codes: `['AUTHORIZATION_CONFIDENCE_LOW', 'CANCEL_RELIABILITY_WEAK', 'CONTAINMENT_WEAK', 'EVIDENCE_VALIDITY_LOW', 'EXTERNAL_SIDE_EFFECT', 'IMPACT_SCOPE_WIDE', 'IRREVERSIBLE_EXPOSURE_HIGH', 'RECOVERY_CAPACITY_LOW', 'REF_GATE_ATTESTATION_VALID_FAILED', 'REF_GATE_OBJECT_SHAPE_EXPECTED_FAILED', 'ROLLBACK_LATENCY_HIGH', 'SENSITIVE_DATA']`
- SPARTa route: `BLOCK`
- Executable: `False`
- Applied controls: `['block_execution', 'preserve_replay', 'explain_denial']`
- DLL valid: `True`

### CLOUD_EXPORT_004_rollout_canary_under_error_budget_pressure

- Description: Read-only kubernetes_rollout_plan export proposes production_canary_rollout in production for deployment.
- Ref gate: `pass`
- Ref failures: `[]`
- Agent identity gate: `WATCH`
- Agent identity reasons: `['AGENT_IDENTITY_MISSING']`
- Scoring admission: `admitted_with_agent_identity_watch`
- SMERC posture: `THROTTLE`
- Scores: `{'irreversible_exposure_score': 0.396, 'reversible_capacity_score': 0.725, 'confidence_score': 0.743, 'operational_stress_score': 0.378, 'risk_adjusted_authorization_score': 0.7, 'cancel_reliability_score': 0.8}`
- Reason codes: `['EXTERNAL_SIDE_EFFECT']`
- SPARTa route: `CONSTRAINED_EXECUTE`
- Executable: `True`
- Applied controls: `['checkpoint_before_execution', 'limit_scope', 'preserve_replay', 'preview_before_execution', 'record_execution_report', 'require_rollback_plan']`
- DLL valid: `True`

### CLOUD_EXPORT_005_cutover_production_dns_endpoint

- Description: Read-only dns_change_request export proposes production_dns_cutover in production for traffic_routing.
- Ref gate: `pass`
- Ref failures: `[]`
- Agent identity gate: `WATCH`
- Agent identity reasons: `['AGENT_IDENTITY_MISSING']`
- Scoring admission: `admitted_with_agent_identity_watch`
- SMERC posture: `THROTTLE`
- Scores: `{'irreversible_exposure_score': 0.613, 'reversible_capacity_score': 0.495, 'confidence_score': 0.676, 'operational_stress_score': 0.529, 'risk_adjusted_authorization_score': 0.522, 'cancel_reliability_score': 0.57}`
- Reason codes: `['IRREVERSIBLE_EXPOSURE_ELEVATED', 'IMPACT_SCOPE_WIDE', 'EXTERNAL_SIDE_EFFECT']`
- SPARTa route: `CONSTRAINED_EXECUTE`
- Executable: `True`
- Applied controls: `['checkpoint_before_execution', 'limit_scope', 'preserve_replay', 'preview_before_execution', 'record_execution_report', 'require_rollback_plan']`
- DLL valid: `True`

### CLOUD_EXPORT_006_shorten_backup_retention_after_cost_anomaly

- Description: Read-only backup_policy_change export proposes backup_retention_reduction in production for resilience.
- Ref gate: `fail`
- Ref failures: `['object_shape_expected']`
- Agent identity gate: `WATCH`
- Agent identity reasons: `['AGENT_IDENTITY_MISSING']`
- Scoring admission: `capped_by_ref_gate`
- SMERC posture: `DENY`
- Scores: `{'irreversible_exposure_score': 0.827, 'reversible_capacity_score': 0.359, 'confidence_score': 0.516, 'operational_stress_score': 0.674, 'risk_adjusted_authorization_score': 0.359, 'cancel_reliability_score': 0.48}`
- Reason codes: `['CONTAINMENT_WEAK', 'EXTERNAL_SIDE_EFFECT', 'IMPACT_SCOPE_WIDE', 'IRREVERSIBLE_EXPOSURE_HIGH', 'RECOVERY_CAPACITY_LOW', 'REF_GATE_OBJECT_SHAPE_EXPECTED_FAILED', 'ROLLBACK_LATENCY_HIGH', 'SENSITIVE_DATA']`
- SPARTa route: `BLOCK`
- Executable: `False`
- Applied controls: `['block_execution', 'preserve_replay', 'explain_denial']`
- DLL valid: `True`

## Autonomy Budget

- State: `SUSPEND_AUTONOMY`
- Spent: `{'actions': 6, 'scope_units': 352.0, 'risk_spend': 5.176, 'ref_gate_failures': 3, 'blocked_or_held_attempts': 3}`
- Review triggers: `['ref_gate_failure', 'risk_budget_exhausted', 'repeated_blocked_or_held_attempts', 'autonomy_removed_until_review']`

## Recommended Next Action

Use these results in a review call and ask the prospect to replace samples with 10 to 25 metadata-only actions from one real workflow.
