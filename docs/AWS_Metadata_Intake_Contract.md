# AWS Metadata Intake Contract

## Purpose

This contract defines the safest first AWS-style input shape for SMERC.

The goal is to let an AWS-style platform, SRE, FinOps, cloud-security, or AI-agent infrastructure reviewer test SMERC with metadata-only exported summaries before any live integration is discussed.

## What It Does

Work:

Accept exported AWS-style action summaries for agent runtime/tool calls, IAM, S3, CloudFormation, drift remediation, RDS, CloudWatch remediation, cost velocity, Secrets Manager rotation, and cross-account delegation.

Result:

The non-executing adapter normalizes accepted summaries into the SMERC customer-evaluation contract, skips unsafe rows, runs recoverability scoring, and produces a reviewer-ready report.

Impact:

A company can test whether SMERC changes action judgment without giving away credentials, account identifiers, raw logs, private topology, customer data, or production access.

## Supported Source Formats

- `agentcore_gateway_tool_call_summary`
- `agentcore_runtime_invocation_summary`
- `iam_policy_change_summary`
- `s3_policy_change_summary`
- `cloudformation_changeset_summary`
- `config_drift_remediation_summary`
- `rds_operation_summary`
- `cloudwatch_remediation_summary`
- `cost_anomaly_action_summary`
- `secrets_rotation_summary`
- `cross_account_delegation_summary`

## Required Fields

Each accepted row must include:

- `record_id`
- `source_format`
- `source_url`
- `workflow_family`
- `environment`
- `actor`
- `tool`
- `proposed_action`
- `aws_surface`
- `requested_capability`
- `current_control`
- `reversibility`
- `containment_strength`
- `rollback_latency`
- `evidence_quality`
- `anomaly_pressure`
- `impact_scope`
- `cancel_reliability`
- `authorization_confidence`
- `least_privilege`
- `max_scope_units`
- `requested_scope_units`
- `side_effect_level`
- `sensitive_data`
- `typed_contract`
- `attestation`
- `object_shape`
- `supports_dry_run`
- `supports_scope_limit`
- `supports_checkpoint`
- `supports_rollback`
- `supports_human_approval`
- `postcondition_evidence_expected`

Ratio fields use `0.0` to `1.0`.

`side_effect_level` must be one of:

- `internal`
- `external`
- `destructive`
- `financial`

`current_control` must be one of:

- `ALLOW`
- `REVIEW`
- `ALERT`
- `BLOCK`

## Recommended AWS/MCP Session Fields

These fields are optional, but they make AWS-style review stronger because they capture how the tool call moved through the gateway and policy session:

- `gateway_only_path`
- `gateway_bypass_detected`
- `delegated_on_behalf_of`
- `principal_type`
- `session_mode`
- `server_initiated_elicitation`
- `server_initiated_sampling`
- `tool_discovery_method`
- `approval_mode`
- `temporal_policy_context`
- `progress_notification_observed`
- `message_notification_observed`

SMERC stores these values in the normalized tool-plan metadata as `session_and_delegated_approval_context`.

Gateway bypass and `approval_mode` of `never` on side-effecting actions also increase base action risk in the AWS metadata adapter. This helps reflect a practical AWS/MCP governance question: did the action flow through the governed gateway and did the session carry enough approval context for the requested side effect?

## Recommended AWS Policy Engine Fields

These fields are optional, but they help AWS-style reviewers map SMERC beside AgentCore Gateway, Gateway Target, Cedar policy, inline tool permissions, and parameter constraints:

- `gateway_target_type`
- `target_registered`
- `policy_language`
- `policy_engine_decision`
- `policy_schema_validated`
- `policy_analysis_result`
- `inline_tool_permissions_present`
- `parameter_constraints_present`

SMERC stores these values in the normalized tool-plan metadata as `agentcore_policy_context`.

Use these fields to show the difference between authorization and recoverability. A policy engine may allow a tool call while SMERC still throttles, freezes, denies, or escalates the action because rollback, blast radius, evidence, or cost velocity is not acceptable.

## Recommended Derived Output Governance Fields

These fields are optional, but they address the MCP governance question of what happens after an authorized tool call produces derived output:

- `input_sensitivity_level`
- `output_sensitivity_level`
- `access_control_composition`
- `regulatory_tags`
- `derived_output_contains_restricted_summary`

SMERC stores these values in the normalized tool-plan metadata as `derived_output_governance`.

Use these fields when a tool result, report, summary, or agent-to-agent handoff may inherit sensitivity from its inputs. The first safe rule is conservative: preserve the highest sensitivity, intersect access controls when multiple sources are combined, and union regulatory or operational tags for downstream review.

## Prohibited Inputs

The first AWS-style pilot should not include:

- AWS account IDs
- ARNs
- access keys
- secret keys
- session tokens
- credentials
- raw CloudTrail events
- raw logs
- private topology
- customer records
- secrets
- production commands
- live AWS API access

Rows containing prohibited fields are skipped by the adapter.

## Run

```bash
python -m reference_engine.aws_metadata_adapter examples/aws_metadata_adapter_source_exports.json --pretty
```

Outputs:

```text
examples/aws_metadata_adapter_normalized_customer_eval_actions.json
reports/aws_metadata_adapter/AWS_Metadata_Adapter_Report.md
reports/aws_metadata_adapter/aws_metadata_adapter_report.json
reports/aws_metadata_adapter/Customer_Evaluation_Report.md
reports/aws_metadata_adapter/customer_evaluation_report.json
```

## Boundary

This is a non-executing adapter stub.

It does not call AWS APIs, assume roles, inspect live accounts, read CloudTrail, execute CloudFormation, modify IAM, access S3, change RDS, trigger remediation, rotate secrets, change cross-account trust, or prove AWS production readiness.

It is not AWS endorsement, AWS certification, compliance evidence, customer validation, incident-reduction proof, or production safety proof.

## Reviewer Question

Can your AWS-style workflow produce 5 to 25 rows in this shape before execution?

If yes, SMERC can run in shadow mode and compare its recoverability posture against existing reviewer judgment.
