# AWS Metadata Adapter Report

Generated: `2026-09-18T00:41:46+00:00`
Version: `smerc.aws-metadata-adapter.v1`

## Purpose

This report shows how an AWS-style platform team could export safe action summaries and run them through SMERC without live AWS access.

The adapter is intentionally non-executing. It accepts metadata summaries, skips unsafe rows, normalizes accepted rows, and then runs SMERC customer evaluation.

## Work / Result / Impact

- Work: Accept safe AWS-style exported summaries and reject unsafe or unsupported rows before scoring.
- Result: Accepted 5 rows, skipped 0 rows, and normalized accepted rows into the SMERC customer-evaluation contract.
- Impact: An AWS-style platform reviewer can test recoverability judgment without granting credentials, sharing sensitive identifiers, or allowing production execution.

## Evidence Boundary

The adapter is a non-executing stub. It does not call AWS APIs, assume roles, inspect live accounts, read CloudTrail, execute CloudFormation, modify IAM, access S3, change RDS, trigger remediation, rotate secrets, or change cross-account trust.

## Adapter Intake

- Source export rows: `5`
- Accepted rows: `5`
- Skipped rows: `0`
- Accepted source formats: `{'agentcore_gateway_tool_call_summary': 1, 'cloudformation_changeset_summary': 1, 'cost_anomaly_action_summary': 1, 'iam_policy_change_summary': 1, 's3_policy_change_summary': 1}`
- Session and delegated approval summary: `{'boolean_counts': {'delegated_on_behalf_of': 1, 'gateway_only_path': 5}, 'principal_type_counts': {'iam_entity': 4, 'oauth_user': 1}, 'session_mode_counts': {'stateful_gateway_session': 2, 'stateless_request': 3}, 'approval_mode_counts': {'required_for_cost_velocity_change': 1, 'required_for_data_access_change': 1, 'required_for_permission_boundary_change': 1, 'required_for_side_effect': 1, 'required_for_stateful_change': 1}}`
- AgentCore runtime security summary: `{'session_user_binding_counts': {}, 'execution_authority_exposure_class_counts': {}, 'command_execution_class_counts': {}, 'boolean_counts': {}}`
- Policy engine summary: `{'boolean_counts': {}, 'policy_engine_decision_counts': {}, 'policy_language_counts': {}, 'gateway_target_type_counts': {}, 'policy_analysis_result_counts': {}}`
- Derived output governance summary: `{'boolean_counts': {}, 'input_sensitivity_counts': {}, 'output_sensitivity_counts': {}, 'access_control_composition_counts': {}, 'regulatory_tag_counts': {}}`
- Environment boundary summary: `{'tooling_isolation_counts': {}, 'host_isolation_counts': {}, 'network_isolation_counts': {}, 'sandbox_escape_surface_counts': {}, 'execution_environment_boundary_counts': {}}`
- Skipped reason counts: `{}`

## Skipped Rows

| Record | Reason |
| --- | --- |

## SMERC Evaluation Summary

- Posture counts: `{'DENY': 3, 'THROTTLE': 2}`
- Route counts: `{'BLOCK': 3, 'CONSTRAINED_EXECUTE': 2}`
- Ref-gate counts: `{'fail': 3, 'pass': 2}`
- Valid DLL ledgers: `5`
- Pilot fit: `strong`

## Highest Exposure Accepted Actions

| Action | Posture | Route | Exposure |
| --- | --- | --- | ---: |
| `AWS_ADAPTER_002_expand_execution_role_permissions` | `DENY` | `BLOCK` | 0.748 |
| `AWS_ADAPTER_004_widen_bucket_policy_access` | `DENY` | `BLOCK` | 0.73 |
| `AWS_ADAPTER_003_execute_stateful_change_set` | `THROTTLE` | `CONSTRAINED_EXECUTE` | 0.645 |
| `AWS_ADAPTER_005_increase_compute_capacity_during_retry_loop` | `DENY` | `BLOCK` | 0.634 |
| `AWS_ADAPTER_001_invoke_action_group_update_config` | `THROTTLE` | `CONSTRAINED_EXECUTE` | 0.586 |

## Reviewer Question

Can your AWS-style workflow produce these safe summaries before execution? If yes, SMERC can be tested in shadow mode without credentials.
