# AWS Metadata Adapter Report

Generated: `2026-09-18T01:12:15+00:00`
Version: `smerc.aws-metadata-adapter.v1`

## Purpose

This report shows how an AWS-style platform team could export safe action summaries and run them through SMERC without live AWS access.

The adapter is intentionally non-executing. It accepts metadata summaries, skips unsafe rows, normalizes accepted rows, and then runs SMERC customer evaluation.

## Work / Result / Impact

- Work: Accept safe AWS-style exported summaries and reject unsafe or unsupported rows before scoring.
- Result: Accepted 8 rows, skipped 0 rows, and normalized accepted rows into the SMERC customer-evaluation contract.
- Impact: An AWS-style platform reviewer can test recoverability judgment without granting credentials, sharing sensitive identifiers, or allowing production execution.

## Evidence Boundary

The adapter is a non-executing stub. It does not call AWS APIs, assume roles, inspect live accounts, read CloudTrail, execute CloudFormation, modify IAM, access S3, change RDS, trigger remediation, rotate secrets, or change cross-account trust.

## Adapter Intake

- Source export rows: `8`
- Accepted rows: `8`
- Skipped rows: `0`
- Accepted source formats: `{'agentcore_gateway_tool_call_summary': 1, 'agentcore_runtime_invocation_summary': 2, 'config_drift_remediation_summary': 1, 'cost_anomaly_action_summary': 1, 'iam_policy_change_summary': 1, 'rds_operation_summary': 1, 's3_policy_change_summary': 1}`
- Session and delegated approval summary: `{'boolean_counts': {}, 'principal_type_counts': {}, 'session_mode_counts': {}, 'approval_mode_counts': {}}`
- AgentCore runtime security summary: `{'session_user_binding_counts': {}, 'execution_authority_exposure_class_counts': {}, 'command_execution_class_counts': {}, 'boolean_counts': {}}`
- Policy engine summary: `{'boolean_counts': {}, 'policy_engine_decision_counts': {}, 'policy_language_counts': {}, 'gateway_target_type_counts': {}, 'policy_analysis_result_counts': {}}`
- Derived output governance summary: `{'boolean_counts': {}, 'input_sensitivity_counts': {}, 'output_sensitivity_counts': {}, 'access_control_composition_counts': {}, 'regulatory_tag_counts': {}}`
- Environment boundary summary: `{'tooling_isolation_counts': {}, 'host_isolation_counts': {}, 'network_isolation_counts': {}, 'sandbox_escape_surface_counts': {}, 'execution_environment_boundary_counts': {}}`
- Skipped reason counts: `{}`

## Skipped Rows

| Record | Reason |
| --- | --- |

## SMERC Evaluation Summary

- Posture counts: `{'DENY': 5, 'THROTTLE': 3}`
- Route counts: `{'BLOCK': 5, 'CONSTRAINED_EXECUTE': 1, 'REVIEW_REQUIRED': 2}`
- Ref-gate counts: `{'fail': 3, 'pass': 5}`
- Valid DLL ledgers: `8`
- Pilot fit: `strong`

## Highest Exposure Accepted Actions

| Action | Posture | Route | Exposure |
| --- | --- | --- | ---: |
| `AWS_ADAPTER_001_delete_an_agentcore_runtime` | `DENY` | `BLOCK` | 0.842 |
| `AWS_ADAPTER_007_reboot_a_production_database_instance` | `DENY` | `BLOCK` | 0.747 |
| `AWS_ADAPTER_008_expand_a_bucket_policy_to_public_read_access` | `DENY` | `BLOCK` | 0.687 |
| `AWS_ADAPTER_003_expand_a_production_execution_role_policy` | `DENY` | `BLOCK` | 0.684 |
| `AWS_ADAPTER_006_open_unrestricted_public_ingress` | `DENY` | `BLOCK` | 0.633 |

## Reviewer Question

Can your AWS-style workflow produce these safe summaries before execution? If yes, SMERC can be tested in shadow mode without credentials.
