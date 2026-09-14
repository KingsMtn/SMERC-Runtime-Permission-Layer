# Customer-Owned Metadata Request

Generated: `2026-09-14T00:58:34+00:00`
Version: `smerc.customer-owned-metadata-request.v1`
Workflow family: `aws`
Requested actions: `12`

## Request

Please replace the public examples with 12 metadata-only actions from one AWS-style cloud automation workflow family.

## Acceptable Action Types

- AgentCore Runtime or Gateway tool invocation
- IAM execution-role or permission-boundary change
- CloudFormation change-set or drift remediation action
- S3 policy, Secrets Manager rotation, RDS, cost-velocity, or cross-account delegation action

## Required Metadata Fields

- `action_id`
- `action_description`
- `actor_or_agent_role`
- `tool_family`
- `environment`
- `requested_scope`
- `current_control_outcome`
- `base_action_risk`
- `reversibility`
- `containment_strength`
- `rollback_latency`
- `evidence_validity`
- `anomaly_pressure`
- `impact_scope`
- `cancel_reliability`
- `authorization_confidence`
- `typed_contract_present`
- `attestation_valid`
- `least_privilege_confirmed`
- `object_shape_valid`

## AWS Recommended Metadata Fields

- `source_format`
- `aws_surface`
- `proposed_action_type`
- `service_family`
- `resource_class`
- `region_scope_count`
- `identity_scope_summary`
- `permission_boundary_present`
- `dry_run_or_preview_available`
- `change_set_or_plan_available`
- `checkpoint_available`
- `rollback_plan_available`
- `gateway_path_enforced`
- `direct_runtime_path_blocked`
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
- `bedrock_guardrail_status`
- `guardrail_decision_summary_available`
- `iam_authorized`
- `dynamic_iam_policy_state`
- `rollback_checkpoint_state`
- `expected_action_chain_evidence`
- `actual_outcome_summary`
- `progress_notification_observed`
- `message_notification_observed`
- `cloudtrail_management_event_expected`
- `cloudtrail_data_event_expected`
- `cloudwatch_metric_or_log_expected`
- `agentcore_trace_or_span_expected`
- `runtime_usage_log_expected`
- `tool_result_metadata_expected`
- `estimated_cost_velocity`
- `cost_anomaly_signal_present`

## Do Not Provide

- secrets, API keys, tokens, passwords, private keys, or wallet keys
- source code bodies, private prompts, model prompts, or proprietary policies
- raw customer records, regulated transaction payloads, AML case files, or sanctions-screening records
- production logs, incident details, account numbers, or confidential infrastructure diagrams
- live credentials or authorization to execute production actions
- AWS account IDs, ARNs, access keys, session tokens, secret values, or credential material
- raw CloudTrail events, raw CloudWatch logs, raw trace bodies, private topology, or production commands
- customer records, regulated payloads, private prompts, proprietary policy bodies, or incident-sensitive details
- permission to assume roles, inspect live accounts, execute change sets, modify IAM, access S3, rotate secrets, or change cross-account trust

## Commands

```bash
python -m reference_engine.customer_evaluation customer_working/customer_actions.json --json-output reports/customer_working/customer_evaluation_report.json --markdown-output reports/customer_working/Customer_Evaluation_Report.md --pretty

python -m reference_engine.aws_metadata_adapter customer_working/aws_source_exports.json --normalized-output reports/customer_working/aws_normalized_customer_actions.json --json-output reports/customer_working/aws_metadata_adapter_report.json --markdown-output reports/customer_working/AWS_Metadata_Adapter_Report.md --customer-json-output reports/customer_working/aws_customer_evaluation_report.json --customer-markdown-output reports/customer_working/AWS_Customer_Evaluation_Report.md --pretty

python -m reference_engine.aws_postcondition_evidence --evaluation reports/customer_working/aws_customer_evaluation_report.json --observations customer_working/aws_postcondition_observations.json --json-output reports/customer_working/aws_postcondition_evidence_report.json --markdown-output reports/customer_working/AWS_Postcondition_Evidence_Report.md --pretty

python -m reference_engine.customer_metadata_validator --checklist customer_working/customer_metadata_substitution_checklist.json --prospect-route customer_working/prospect_route.json --customer-intake customer_working/customer_action_intake.json --pilot-handoff customer_working/pilot_handoff.json --pretty

python -m reference_engine.serious_report_performance --iterations 5 --pretty
```

## Reviewer Questions

- Which SMERC posture matched current reviewer judgment?
- Which action was usefully constrained instead of simply allowed or blocked?
- Which action failed because evidence was missing or untrusted?
- Which p95 workflow overhead would make this unsuitable?
- Would these results justify a bounded shadow-mode pilot?

## AWS Reviewer Questions

- Can these AWS-style actions be reviewed without account IDs, ARNs, raw logs, secrets, or live access?
- Which action should be constrained instead of allowed or blocked outright?
- Which Bedrock-style guardrail pass still needed a SMERC recoverability check before IAM, Systems Manager, CloudFormation, CloudWatch, or cost-sensitive execution?
- Which postcondition evidence source would prove the required control happened?
- Which control is hardest to prove: preview, scope limit, checkpoint, rollback plan, gateway enforcement, block, replay, or cost-velocity bound?
- Would these results justify a bounded AWS shadow-mode pilot where existing AWS/customer controls remain authoritative?

## Work / Result / Impact

- Work: Ask an AWS-style platform reviewer to supply safe metadata-only action summaries and matching postcondition observation summaries from one real workflow.
- Result: SMERC can compare customer-owned action metadata against its public examples, posture logic, SPARTa routes, postcondition evidence expectations, and local performance metrics.
- Impact: The project can move from synthetic proof toward reviewer-owned evidence without requesting secrets, production access, regulated payloads, or enforcement authority.

## Evidence Boundary

Customer-owned metadata review is still pre-production and shadow-mode. It does not prove customer demand, incident reduction, compliance, production safety, or enforce-mode readiness.
