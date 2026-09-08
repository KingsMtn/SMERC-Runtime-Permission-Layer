# AWS Metadata Adapter Report

Generated: `2026-09-08T01:12:12+00:00`
Version: `smerc.aws-metadata-adapter.v1`

## Purpose

This report shows how an AWS-style platform team could export safe action summaries and run them through SMERC without live AWS access.

The adapter is intentionally non-executing. It accepts metadata summaries, skips unsafe rows, normalizes accepted rows, and then runs SMERC customer evaluation.

## Work / Result / Impact

- Work: Accept safe AWS-style exported summaries and reject unsafe or unsupported rows before scoring.
- Result: Accepted 6 rows, skipped 2 rows, and normalized accepted rows into the SMERC customer-evaluation contract.
- Impact: An AWS-style platform reviewer can test recoverability judgment without granting credentials, sharing sensitive identifiers, or allowing production execution.

## Evidence Boundary

The adapter is a non-executing stub. It does not call AWS APIs, assume roles, inspect live accounts, read CloudTrail, execute CloudFormation, modify IAM, access S3, change RDS, trigger remediation, rotate secrets, or change cross-account trust.

## Adapter Intake

- Source export rows: `8`
- Accepted rows: `6`
- Skipped rows: `2`
- Accepted source formats: `{'agentcore_gateway_tool_call_summary': 1, 'cloudformation_changeset_summary': 1, 'cost_anomaly_action_summary': 1, 'iam_policy_change_summary': 1, 's3_policy_change_summary': 1, 'secrets_rotation_summary': 1}`
- Session and delegated approval summary: `{'boolean_counts': {'delegated_on_behalf_of': 2, 'gateway_bypass_detected': 1, 'gateway_only_path': 5, 'message_notification_observed': 5, 'progress_notification_observed': 4, 'server_initiated_elicitation': 3}, 'principal_type_counts': {'iam_entity': 4, 'oauth_user': 2}, 'session_mode_counts': {'stateful_gateway_session': 2, 'stateless_request': 4}, 'approval_mode_counts': {'never': 1, 'required_for_data_access_change': 1, 'required_for_permission_boundary_change': 1, 'required_for_secret_rotation': 1, 'required_for_side_effect': 1, 'required_for_stateful_replacement': 1}}`
- Skipped reason counts: `{'prohibited field present: raw_log': 1, 'unsupported source_format': 1}`

## Skipped Rows

| Record | Reason |
| --- | --- |
| `aws-meta-007-unsafe` | prohibited field present: raw_log |
| `aws-meta-008-unsupported` | unsupported source_format |

## SMERC Evaluation Summary

- Posture counts: `{'DENY': 1, 'THROTTLE': 5}`
- Route counts: `{'BLOCK': 1, 'CONSTRAINED_EXECUTE': 5}`
- Ref-gate counts: `{'fail': 1, 'pass': 5}`
- Valid DLL ledgers: `6`
- Pilot fit: `strong`

## Highest Exposure Accepted Actions

| Action | Posture | Route | Exposure |
| --- | --- | --- | ---: |
| `AWS_ADAPTER_003_execute_change_set_that_replaces_stateful_resources` | `THROTTLE` | `CONSTRAINED_EXECUTE` | 0.755 |
| `AWS_ADAPTER_002_expand_execution_role_from_service_update_scope_to_broad_infrastructure_` | `DENY` | `BLOCK` | 0.748 |
| `AWS_ADAPTER_005_widen_bucket_object_access_during_failed_data_export` | `THROTTLE` | `CONSTRAINED_EXECUTE` | 0.73 |
| `AWS_ADAPTER_006_rotate_shared_service_credential_before_dependency_readiness_is_confirme` | `THROTTLE` | `CONSTRAINED_EXECUTE` | 0.658 |
| `AWS_ADAPTER_001_invoke_lambda_backed_customer_configuration_tool_through_governed_gatewa` | `THROTTLE` | `CONSTRAINED_EXECUTE` | 0.586 |

## Reviewer Question

Can your AWS-style workflow produce these safe summaries before execution? If yes, SMERC can be tested in shadow mode without credentials.
