# AWS Metadata Adapter Report

Generated: `2026-09-15T23:50:11+00:00`
Version: `smerc.aws-metadata-adapter.v1`

## Purpose

This report shows how an AWS-style platform team could export safe action summaries and run them through SMERC without live AWS access.

The adapter is intentionally non-executing. It accepts metadata summaries, skips unsafe rows, normalizes accepted rows, and then runs SMERC customer evaluation.

## Work / Result / Impact

- Work: Accept safe AWS-style exported summaries and reject unsafe or unsupported rows before scoring.
- Result: Accepted 9 rows, skipped 2 rows, and normalized accepted rows into the SMERC customer-evaluation contract.
- Impact: An AWS-style platform reviewer can test recoverability judgment without granting credentials, sharing sensitive identifiers, or allowing production execution.

## Evidence Boundary

The adapter is a non-executing stub. It does not call AWS APIs, assume roles, inspect live accounts, read CloudTrail, execute CloudFormation, modify IAM, access S3, change RDS, trigger remediation, rotate secrets, or change cross-account trust.

## Adapter Intake

- Source export rows: `11`
- Accepted rows: `9`
- Skipped rows: `2`
- Accepted source formats: `{'agentcore_gateway_tool_call_summary': 1, 'agentcore_runtime_invocation_summary': 3, 'cloudformation_changeset_summary': 1, 'cost_anomaly_action_summary': 1, 'iam_policy_change_summary': 1, 's3_policy_change_summary': 1, 'secrets_rotation_summary': 1}`
- Session and delegated approval summary: `{'boolean_counts': {'delegated_on_behalf_of': 4, 'gateway_bypass_detected': 3, 'gateway_only_path': 6, 'message_notification_observed': 7, 'progress_notification_observed': 6, 'server_initiated_elicitation': 3}, 'principal_type_counts': {'iam_entity': 5, 'oauth_user': 3, 'shared_backend_iam_role': 1}, 'session_mode_counts': {'runtime_command_session': 1, 'stateful_gateway_session': 2, 'stateful_runtime_session': 2, 'stateless_request': 4}, 'approval_mode_counts': {'never': 2, 'required_for_data_access_change': 1, 'required_for_permission_boundary_change': 1, 'required_for_secret_rotation': 1, 'required_for_shell': 1, 'required_for_side_effect': 2, 'required_for_stateful_replacement': 1}}`
- AgentCore runtime security summary: `{'session_user_binding_counts': {'client_supplied_unverified': 1, 'iam_principal_bound_request': 4, 'jwt_verified_user_session': 3, 'shared_principal_unbound': 1}, 'execution_authority_exposure_class_counts': {'broad_execution_role': 2, 'runtime_metadata_credentials': 2, 'scoped_execution_role': 1, 'scoped_gateway_identity': 3, 'scoped_infrastructure_role': 1}, 'command_execution_class_counts': {'interactive_shell': 1, 'none': 8}, 'boolean_counts': {'audit_correlation_available': 7, 'audit_correlation_missing': 2}}`
- Policy engine summary: `{'boolean_counts': {'inline_tool_permissions_present': 7, 'parameter_constraints_present': 6, 'policy_schema_validated': 9, 'target_registered': 8}, 'policy_engine_decision_counts': {'allow': 2, 'allow_with_constraints': 6, 'deny': 1}, 'policy_language_counts': {'cedar': 9}, 'gateway_target_type_counts': {'agentcore_runtime': 2, 'lambda': 3, 'openapi': 2, 'runtime_command': 1, 'smithy_model': 1}, 'policy_analysis_result_counts': {'bounded_policy': 1, 'command_execution_requires_audit_and_scope': 1, 'data_access_requires_scope_bound': 1, 'dependency_readiness_required': 1, 'missing_cost_velocity_constraint': 1, 'missing_session_user_binding': 1, 'overbroad_permission_boundary': 1, 'session_bound_gateway_path': 1, 'stateful_replacement_requires_review': 1}}`
- Derived output governance summary: `{'boolean_counts': {'restricted_summary_outputs': 5}, 'input_sensitivity_counts': {'customer_data': 3, 'operational_cost': 1, 'privileged_infrastructure': 2, 'restricted_data': 1, 'secret_reference': 1, 'service_state': 1}, 'output_sensitivity_counts': {'customer_data': 3, 'operational_cost': 1, 'privileged_infrastructure': 2, 'restricted_data': 1, 'secret_reference': 1, 'service_state': 1}, 'access_control_composition_counts': {'intersect_access_controls': 2, 'max_sensitivity_intersect_access': 1, 'max_sensitivity_union_tags': 1, 'preserve_highest_sensitivity': 1, 'preserve_secret_boundary': 1, 'runtime_execution_role_boundary': 1, 'shared_principal_runtime_session': 1, 'union_cost_and_runtime_tags': 1}, 'regulatory_tag_counts': {'agent-session': 2, 'change-management': 1, 'customer-data': 1, 'data-access': 1, 'finops': 1, 'privacy': 4, 'privileged-access': 2, 'resilience': 1, 'runtime-command': 1, 'runtime-cost': 1, 'runtime-risk': 1, 'secret-management': 1, 'service-auth': 1, 'sox': 1}}`
- Environment boundary summary: `{'tooling_isolation_counts': {'privileged_automation': 1, 'restricted_tools': 1}, 'host_isolation_counts': {'container': 1, 'dedicated_account': 1}, 'network_isolation_counts': {'production_network': 1, 'scoped_private_network': 1}, 'sandbox_escape_surface_counts': {'cloud_metadata_access': 1, 'none_known': 1, 'production_credentials': 1}, 'execution_environment_boundary_counts': {'bedrock_action_group': 1, 'ci_runner': 1}}`
- Skipped reason counts: `{'prohibited field present: raw_log': 1, 'unsupported source_format': 1}`

## Skipped Rows

| Record | Reason |
| --- | --- |
| `aws-meta-007-unsafe` | prohibited field present: raw_log |
| `aws-meta-008-unsupported` | unsupported source_format |

## SMERC Evaluation Summary

- Posture counts: `{'DENY': 3, 'THROTTLE': 6}`
- Route counts: `{'BLOCK': 3, 'CONSTRAINED_EXECUTE': 6}`
- Ref-gate counts: `{'fail': 3, 'pass': 6}`
- Valid DLL ledgers: `9`
- Pilot fit: `strong`

## Highest Exposure Accepted Actions

| Action | Posture | Route | Exposure |
| --- | --- | --- | ---: |
| `AWS_ADAPTER_009_open_interactive_command_shell_in_runtime_with_broad_execution_role_cred` | `DENY` | `BLOCK` | 0.911 |
| `AWS_ADAPTER_008_invoke_runtime_using_client_supplied_session_identifier_under_shared_bac` | `DENY` | `BLOCK` | 0.872 |
| `AWS_ADAPTER_002_expand_execution_role_from_service_update_scope_to_broad_infrastructure_` | `DENY` | `BLOCK` | 0.783 |
| `AWS_ADAPTER_003_execute_change_set_that_replaces_stateful_resources` | `THROTTLE` | `CONSTRAINED_EXECUTE` | 0.755 |
| `AWS_ADAPTER_005_widen_bucket_object_access_during_failed_data_export` | `THROTTLE` | `CONSTRAINED_EXECUTE` | 0.73 |

## Reviewer Question

Can your AWS-style workflow produce these safe summaries before execution? If yes, SMERC can be tested in shadow mode without credentials.
