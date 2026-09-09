# AWS Postcondition Evidence Report

Generated: `2026-09-09T22:00:04+00:00`
Version: `smerc.aws-postcondition-evidence.v1`

## Purpose

This report shows how AWS-style observation metadata could prove whether SMERC-required controls actually happened after a route decision.

## Work / Result / Impact

- Work: Compare SMERC/SPARTa route controls for AWS-style actions against safe postcondition observations modeled on CloudTrail, CloudWatch, AgentCore Gateway, AgentCore Runtime, MCP gateway logs, and native AWS change records.
- Result: Assessed 6 AWS-style routed actions, observed 6, and found AWS postcondition statuses {'gap': 2, 'pass': 4}.
- Impact: SMERC can now show how an AWS-style governed action bot would prove that controls were actually applied after a decision, not only that recoverability scoring recommended them.

## AWS Signal Surfaces Modeled

- Amazon Bedrock AgentCore Gateway CloudTrail management events
- Amazon Bedrock AgentCore Gateway CloudTrail data events for InvokeGateway when explicitly enabled
- Amazon Bedrock AgentCore Runtime and Gateway CloudWatch logs, metrics, and spans
- AgentCore runtime usage logs with one-second CPU and memory usage fields
- AgentCore tool result metadata stream entries
- AgentCore Gateway MCP logging notifications
- native AWS change records such as IAM, CloudFormation, S3, Secrets Manager, and cost anomaly summaries

## Evidence Boundary

This is metadata-only AWS-style postcondition evidence. It does not call AWS APIs, read live AWS accounts, collect raw CloudTrail, collect raw CloudWatch logs, expose account IDs, expose ARNs, or prove AWS production enforcement. It shows what safe observation fields a customer or AWS-style reviewer could export to prove that SMERC-required controls happened after routing.

## Summary

- Evaluated actions: `6`
- Observed actions: `6`
- AWS postcondition status counts: `{'gap': 2, 'pass': 4}`
- Observed AWS evidence sources: `{'agentcore_gateway_cloudtrail_data_event': 1, 'agentcore_gateway_mcp_log': 1, 'agentcore_runtime_trace_span': 1, 'agentcore_runtime_usage_log': 1, 'cloudformation_change_set_record': 1, 'cloudtrail_management_event': 4, 'cloudwatch_metric_or_log': 2, 'cost_anomaly_signal': 1, 'iam_access_analyzer_or_policy_record': 1, 's3_policy_audit_record': 1, 'secrets_rotation_record': 1, 'tool_result_metadata_stream': 1}`
- Missing AWS evidence sources: `{'cloudwatch_metric_or_log': 1}`

## Action Checks

| Action | AWS surface | Route | Execution | Missing route controls | Missing AWS sources | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `AWS_ADAPTER_001_invoke_lambda_backed_customer_configuration_tool_through_governed_gatewa` | `agentcore_gateway_tool_call_summary` | `CONSTRAINED_EXECUTE` | `succeeded` | `[]` | `[]` | `pass` |
| `AWS_ADAPTER_002_expand_execution_role_from_service_update_scope_to_broad_infrastructure_` | `iam_policy_change_summary` | `BLOCK` | `not_executed` | `[]` | `[]` | `pass` |
| `AWS_ADAPTER_003_execute_change_set_that_replaces_stateful_resources` | `cloudformation_changeset_summary` | `CONSTRAINED_EXECUTE` | `succeeded` | `[]` | `['cloudwatch_metric_or_log']` | `gap` |
| `AWS_ADAPTER_004_increase_regional_compute_capacity_while_completion_certainty_is_low` | `cost_anomaly_action_summary` | `CONSTRAINED_EXECUTE` | `succeeded` | `[]` | `[]` | `pass` |
| `AWS_ADAPTER_005_widen_bucket_object_access_during_failed_data_export` | `s3_policy_change_summary` | `CONSTRAINED_EXECUTE` | `succeeded` | `['require_rollback_plan']` | `[]` | `gap` |
| `AWS_ADAPTER_006_rotate_shared_service_credential_before_dependency_readiness_is_confirme` | `secrets_rotation_summary` | `CONSTRAINED_EXECUTE` | `succeeded` | `[]` | `[]` | `pass` |

## Reviewer Question

For one AWS-style workflow, can the platform export safe observation metadata that proves preview, scope limit, checkpoint, rollback plan, gateway enforcement, execution block, replay, cost-velocity, and trace evidence without exposing secrets or raw customer logs?
