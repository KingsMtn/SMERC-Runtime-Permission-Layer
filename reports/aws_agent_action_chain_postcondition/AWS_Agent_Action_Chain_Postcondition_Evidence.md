# AWS Agent Action Chain Postcondition Evidence

Generated: `2026-09-09T01:06:13+00:00`
Version: `smerc.aws-agent-action-chain-postcondition.v1`

## Purpose

This report shows whether AWS-style action-chain observation metadata can prove that SMERC-required controls actually happened after the recoverability route.

## Work / Result / Impact

- Work: Run AWS-style agent action chains through SMERC, then compare the required route controls with safe postcondition observations modeled on guardrail, IAM, Systems Manager, CloudFormation, CloudWatch, cost, CloudTrail, runtime, and tool-result evidence.
- Result: Evaluated 5 action chains and assessed 5 postcondition observation sets with statuses {'gap': 1, 'pass': 4}.
- Impact: SMERC can show not only where the recoverability gate sits, but also what evidence would prove that slowed, blocked, or constrained AWS-style actions actually followed the required route.

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

- Evaluated actions: `5`
- Observed actions: `5`
- AWS postcondition status counts: `{'gap': 1, 'pass': 4}`
- Observed AWS evidence sources: `{'agentcore_gateway_cloudtrail_data_event': 1, 'agentcore_gateway_mcp_log': 1, 'agentcore_runtime_usage_log': 1, 'cloudformation_change_set_record': 1, 'cloudtrail_management_event': 4, 'cloudwatch_metric_or_log': 3, 'cost_anomaly_signal': 1, 'iam_access_analyzer_or_policy_record': 1, 'tool_result_metadata_stream': 1}`
- Missing AWS evidence sources: `{'cloudwatch_metric_or_log': 1}`

## Action Checks

| Action | AWS surface | Route | Execution | Missing route controls | Missing AWS sources | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `AWS_CHAIN_SAFE_CONFIG_UPDATE_001` | `systems_manager_execution_summary` | `CONSTRAINED_EXECUTE` | `succeeded` | `[]` | `[]` | `pass` |
| `AWS_CHAIN_GUARDRAIL_PASS_IAM_WIDE_002` | `iam_policy_change_summary` | `BLOCK` | `not_executed` | `[]` | `[]` | `pass` |
| `AWS_CHAIN_CLOUDFORMATION_REPLACE_003` | `cloudformation_changeset_summary` | `BLOCK` | `not_executed` | `[]` | `['cloudwatch_metric_or_log']` | `gap` |
| `AWS_CHAIN_CLOUDWATCH_REMEDIATION_004` | `cloudwatch_remediation_summary` | `BLOCK` | `not_executed` | `[]` | `[]` | `pass` |
| `AWS_CHAIN_COST_SCALE_SPIKE_005` | `cost_velocity_action_summary` | `CONSTRAINED_EXECUTE` | `succeeded` | `[]` | `[]` | `pass` |

## Reviewer Question

For one AWS-style workflow, can the platform export safe observation metadata that proves preview, scope limit, checkpoint, rollback plan, gateway enforcement, execution block, replay, cost-velocity, and trace evidence without exposing secrets or raw customer logs?
