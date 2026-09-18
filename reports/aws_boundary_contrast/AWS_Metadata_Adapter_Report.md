# AWS Metadata Adapter Report

Generated: `2026-09-18T01:22:16+00:00`
Version: `smerc.aws-metadata-adapter.v1`

## Purpose

This report shows how an AWS-style platform team could export safe action summaries and run them through SMERC without live AWS access.

The adapter is intentionally non-executing. It accepts metadata summaries, skips unsafe rows, normalizes accepted rows, and then runs SMERC customer evaluation.

## Work / Result / Impact

- Work: Accept safe AWS-style exported summaries and reject unsafe or unsupported rows before scoring.
- Result: Accepted 4 rows, skipped 0 rows, and normalized accepted rows into the SMERC customer-evaluation contract.
- Impact: An AWS-style platform reviewer can test recoverability judgment without granting credentials, sharing sensitive identifiers, or allowing production execution.

## Evidence Boundary

The adapter is a non-executing stub. It does not call AWS APIs, assume roles, inspect live accounts, read CloudTrail, execute CloudFormation, modify IAM, access S3, change RDS, trigger remediation, rotate secrets, or change cross-account trust.

## Adapter Intake

- Source export rows: `4`
- Accepted rows: `4`
- Skipped rows: `0`
- Accepted source formats: `{'agentcore_gateway_tool_call_summary': 2, 'agentcore_runtime_invocation_summary': 2}`
- Session and delegated approval summary: `{'boolean_counts': {}, 'principal_type_counts': {}, 'session_mode_counts': {}, 'approval_mode_counts': {}}`
- AgentCore runtime security summary: `{'session_user_binding_counts': {}, 'execution_authority_exposure_class_counts': {}, 'command_execution_class_counts': {}, 'boolean_counts': {}}`
- Policy engine summary: `{'boolean_counts': {}, 'policy_engine_decision_counts': {}, 'policy_language_counts': {}, 'gateway_target_type_counts': {}, 'policy_analysis_result_counts': {}}`
- Derived output governance summary: `{'boolean_counts': {}, 'input_sensitivity_counts': {}, 'output_sensitivity_counts': {}, 'access_control_composition_counts': {}, 'regulatory_tag_counts': {}}`
- Environment boundary summary: `{'tooling_isolation_counts': {'privileged_automation': 2, 'restricted_tools': 2}, 'host_isolation_counts': {'hardened_container': 2, 'process': 2}, 'network_isolation_counts': {'production_network': 2, 'scoped_private_network': 2}, 'sandbox_escape_surface_counts': {'cloud_metadata_access': 2, 'none_known': 2, 'production_credentials': 2}, 'execution_environment_boundary_counts': {'cloud_function': 2, 'production_host': 2}}`
- Skipped reason counts: `{}`

## Skipped Rows

| Record | Reason |
| --- | --- |

## SMERC Evaluation Summary

- Posture counts: `{'FREEZE': 2, 'THROTTLE': 2}`
- Route counts: `{'PAUSE': 2, 'REVIEW_REQUIRED': 2}`
- Ref-gate counts: `{'pass': 4}`
- Valid DLL ledgers: `4`
- Pilot fit: `moderate`

## Highest Exposure Accepted Actions

| Action | Posture | Route | Exposure |
| --- | --- | --- | ---: |
| `AWS_ADAPTER_002_create_a_billable_agentcore_runtime` | `FREEZE` | `PAUSE` | 0.487 |
| `AWS_ADAPTER_001_create_a_billable_agentcore_runtime` | `THROTTLE` | `REVIEW_REQUIRED` | 0.459 |
| `AWS_ADAPTER_004_invoke_a_bedrock_model_with_bounded_input` | `FREEZE` | `PAUSE` | 0.428 |
| `AWS_ADAPTER_003_invoke_a_bedrock_model_with_bounded_input` | `THROTTLE` | `REVIEW_REQUIRED` | 0.401 |

## Reviewer Question

Can your AWS-style workflow produce these safe summaries before execution? If yes, SMERC can be tested in shadow mode without credentials.
