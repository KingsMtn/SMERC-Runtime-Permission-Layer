# AWS Cloud Action Replay

Generated: `2026-09-07T16:59:41+00:00`
Version: `smerc.aws-cloud-action-replay.v1`

## Purpose

This proof pack shows how SMERC evaluates AWS-style cloud and AI-agent infrastructure actions before they change runtime behavior, permissions, data access, infrastructure state, database resources, remediation paths, cross-account trust, or spend velocity.

The useful question is narrow: after normal authorization says an action can be attempted, is this specific action recoverable, bounded, evidenced, and safe to proceed right now?

## Evidence Boundary

AWS Cloud Action Replay uses metadata-only AWS-style examples. It does not connect to AWS, invoke AgentCore, read CloudTrail, inspect CloudFormation stacks, call IAM, access S3, change RDS, execute CloudWatch remediation, rotate credentials, move funds, create infrastructure, or use customer telemetry. It is not AWS endorsement, AWS certification, production-readiness proof, or incident-reduction proof.

## Work / Result / Impact

Work: run twelve AWS-style metadata actions through SMERC's customer-evaluation contract, hard evidence gates, recoverability scoring, Governance Routing Workbench routes, autonomy budgeting, and Decision Lifecycle Ledger proof.

Result: `12` actions evaluated with posture counts `{'ALLOW': 1, 'DENY': 5, 'THROTTLE': 6}`, route counts `{'BLOCK': 5, 'CONSTRAINED_EXECUTE': 6, 'EXECUTE': 1}`, and `12` valid ledgers.

Impact: a reviewer can see where authorized cloud or agent actions should be allowed, slowed, paused, blocked, or escalated before side effects occur. This turns the AWS discussion into a runnable proof instead of a pitch.

## Summary

- Actions evaluated: `12`
- Posture counts: `{'ALLOW': 1, 'DENY': 5, 'THROTTLE': 6}`
- Route state counts: `{'BLOCK': 5, 'CONSTRAINED_EXECUTE': 6, 'EXECUTE': 1}`
- Ref-gate counts: `{'fail': 5, 'pass': 7}`
- Agent identity-gate counts: `{'WATCH': 12}`
- Non-executable routes: `5`
- Valid DLL ledgers: `12`
- Autonomy state: `SUSPEND_AUTONOMY`
- Pilot fit: `strong`

## AWS-Style Surfaces

| Surface | Count | Alignment |
| --- | ---: | --- |
| `bedrock_agentcore_gateway` | 1 | Amazon Bedrock AgentCore Gateway-style governed entry point, policy, guardrail, and interceptor path. |
| `bedrock_agentcore_runtime` | 1 | Amazon Bedrock AgentCore Runtime-style session, invocation, identity, and runtime isolation path. |
| `cloudformation` | 2 | AWS CloudFormation change set and drift-aware change-management path. |
| `cloudwatch` | 1 | Amazon CloudWatch-style alarm, telemetry, and automated-remediation path. |
| `cost_management` | 1 | AWS cost-management and FinOps-style spend-velocity path. |
| `ecs` | 1 | Amazon ECS/Fargate-style service capacity and deployment-control path. |
| `iam` | 1 | AWS IAM least-privilege and role-policy path. |
| `rds` | 1 | Amazon RDS-style stateful data-plane administration path. |
| `resource_policy` | 1 | AWS resource-based policy and cross-account access path. |
| `s3` | 1 | Amazon S3-style data access and bucket-policy path. |
| `secrets_manager` | 1 | AWS Secrets Manager-style rotation and service-authentication path. |

## AWS Reason Codes

| Reason code | Count | Meaning |
| --- | ---: | --- |
| `AGENTCORE_GATEWAY_BYPASS_RISK` | 1 | The request shape suggests an agent runtime path that bypasses a governed gateway, interceptor, or policy choke point. |
| `AGENTCORE_TOOL_SIDE_EFFECT` | 2 | The action invokes an agent tool target that can create external or customer-facing side effects. |
| `AUTOMATED_REMEDIATION_PRESSURE` | 2 | The action is triggered by operational pressure, where speed is useful but evidence and rollback still matter. |
| `CLOUDFORMATION_REPLACEMENT_RISK` | 2 | The infrastructure change may replace or recreate resources rather than only update reversible configuration. |
| `COST_VELOCITY_SPIKE` | 1 | The action can increase spend velocity faster than confidence in task completion or containment. |
| `CROSS_ACCOUNT_DELEGATION_RISK` | 1 | The action can extend trust or invocation authority across account boundaries. |
| `DRIFT_RECONCILIATION_RISK` | 1 | The action remediates drift where the live state may contain unmodeled operational intent. |
| `ECS_CAPACITY_SHIFT` | 1 | The action changes service capacity or regional placement while reliability evidence matters. |
| `EVIDENCE_INCOMPLETE` | 8 | Trusted evidence is not strong enough to support confident execution. |
| `IAM_SCOPE_EXPANSION` | 1 | The action can expand what a principal, role, runtime, or workload may do later. |
| `PRODUCTION_BLAST_RADIUS_WIDE` | 8 | The action targets production with broad enough scope to create meaningful blast radius. |
| `RDS_DATA_PLANE_RECOVERY_RISK` | 1 | The action touches stateful database resources where recovery path, snapshots, and rollback latency matter. |
| `ROLLBACK_UNCERTAIN` | 6 | Rollback, cancellation, or checkpoint support is weak for the proposed action. |
| `S3_POLICY_EXPOSURE` | 1 | The action can widen object, bucket, or data-access exposure. |
| `SECRETS_ROTATION_IMPACT` | 1 | Authentication material changes can interrupt dependent services if coordination or rollback fails. |

## Scenario Results

| Action | Surface | Posture | Route | Exposure | Reason codes |
| --- | --- | --- | --- | ---: | --- |
| `AWS_AGENTCORE_TOOL_LAMBDA_001` | `bedrock_agentcore_gateway` | `THROTTLE` | `CONSTRAINED_EXECUTE` | 0.618 | `AGENTCORE_TOOL_SIDE_EFFECT` |
| `AWS_AGENTCORE_GATEWAY_BYPASS_002` | `bedrock_agentcore_runtime` | `DENY` | `BLOCK` | 0.807 | `AGENTCORE_GATEWAY_BYPASS_RISK`, `AGENTCORE_TOOL_SIDE_EFFECT`, `EVIDENCE_INCOMPLETE`, `PRODUCTION_BLAST_RADIUS_WIDE`, `ROLLBACK_UNCERTAIN` |
| `AWS_IAM_ROLE_EXPANSION_003` | `iam` | `DENY` | `BLOCK` | 0.792 | `EVIDENCE_INCOMPLETE`, `IAM_SCOPE_EXPANSION`, `PRODUCTION_BLAST_RADIUS_WIDE`, `ROLLBACK_UNCERTAIN` |
| `AWS_S3_POLICY_PUBLIC_EXPOSURE_004` | `s3` | `THROTTLE` | `CONSTRAINED_EXECUTE` | 0.759 | `EVIDENCE_INCOMPLETE`, `PRODUCTION_BLAST_RADIUS_WIDE`, `S3_POLICY_EXPOSURE` |
| `AWS_CFN_CHANGESET_REPLACE_005` | `cloudformation` | `THROTTLE` | `CONSTRAINED_EXECUTE` | 0.763 | `CLOUDFORMATION_REPLACEMENT_RISK`, `PRODUCTION_BLAST_RADIUS_WIDE`, `ROLLBACK_UNCERTAIN` |
| `AWS_CFN_DRIFT_REMEDIATE_006` | `cloudformation` | `DENY` | `BLOCK` | 0.597 | `AUTOMATED_REMEDIATION_PRESSURE`, `CLOUDFORMATION_REPLACEMENT_RISK`, `DRIFT_RECONCILIATION_RISK`, `EVIDENCE_INCOMPLETE`, `ROLLBACK_UNCERTAIN` |
| `AWS_ECS_SCALE_SHIFT_007` | `ecs` | `ALLOW` | `EXECUTE` | 0.31 | `ECS_CAPACITY_SHIFT` |
| `AWS_RDS_CLUSTER_DELETE_008` | `rds` | `DENY` | `BLOCK` | 0.968 | `EVIDENCE_INCOMPLETE`, `PRODUCTION_BLAST_RADIUS_WIDE`, `RDS_DATA_PLANE_RECOVERY_RISK`, `ROLLBACK_UNCERTAIN` |
| `AWS_CLOUDWATCH_REMEDIATE_009` | `cloudwatch` | `THROTTLE` | `CONSTRAINED_EXECUTE` | 0.623 | `AUTOMATED_REMEDIATION_PRESSURE`, `EVIDENCE_INCOMPLETE`, `PRODUCTION_BLAST_RADIUS_WIDE` |
| `AWS_COST_VELOCITY_SPIKE_010` | `cost_management` | `THROTTLE` | `CONSTRAINED_EXECUTE` | 0.551 | `COST_VELOCITY_SPIKE`, `EVIDENCE_INCOMPLETE`, `PRODUCTION_BLAST_RADIUS_WIDE` |
| `AWS_SECRETS_ROTATION_011` | `secrets_manager` | `THROTTLE` | `CONSTRAINED_EXECUTE` | 0.481 | `SECRETS_ROTATION_IMPACT` |
| `AWS_CROSS_ACCOUNT_DELEGATION_012` | `resource_policy` | `DENY` | `BLOCK` | 0.766 | `CROSS_ACCOUNT_DELEGATION_RISK`, `EVIDENCE_INCOMPLETE`, `PRODUCTION_BLAST_RADIUS_WIDE`, `ROLLBACK_UNCERTAIN` |

## Reviewer Examples

| Work | Result | Impact |
| --- | --- | --- |
| Evaluate AWS-style `bedrock_agentcore_gateway` action `AWS_AGENTCORE_TOOL_LAMBDA_001` before execution using hard evidence gates, recoverability scoring, Governance Routing Workbench routes, and Decision Lifecycle Ledger evidence. | SMERC returned `THROTTLE`, routed `CONSTRAINED_EXECUTE`, and assigned AWS reason codes AGENTCORE_TOOL_SIDE_EFFECT. | The action can continue only through constrained execution such as scope limits, preview, checkpointing, or rate limits. Irreversible exposure score: 0.618. |
| Evaluate AWS-style `bedrock_agentcore_runtime` action `AWS_AGENTCORE_GATEWAY_BYPASS_002` before execution using hard evidence gates, recoverability scoring, Governance Routing Workbench routes, and Decision Lifecycle Ledger evidence. | SMERC returned `DENY`, routed `BLOCK`, and assigned AWS reason codes AGENTCORE_GATEWAY_BYPASS_RISK, AGENTCORE_TOOL_SIDE_EFFECT, EVIDENCE_INCOMPLETE, PRODUCTION_BLAST_RADIUS_WIDE, ROLLBACK_UNCERTAIN. | The action is blocked until the request is repaired, narrowed, or resubmitted with stronger evidence. Irreversible exposure score: 0.807. |
| Evaluate AWS-style `iam` action `AWS_IAM_ROLE_EXPANSION_003` before execution using hard evidence gates, recoverability scoring, Governance Routing Workbench routes, and Decision Lifecycle Ledger evidence. | SMERC returned `DENY`, routed `BLOCK`, and assigned AWS reason codes EVIDENCE_INCOMPLETE, IAM_SCOPE_EXPANSION, PRODUCTION_BLAST_RADIUS_WIDE, ROLLBACK_UNCERTAIN. | The action is blocked until the request is repaired, narrowed, or resubmitted with stronger evidence. Irreversible exposure score: 0.792. |
| Evaluate AWS-style `s3` action `AWS_S3_POLICY_PUBLIC_EXPOSURE_004` before execution using hard evidence gates, recoverability scoring, Governance Routing Workbench routes, and Decision Lifecycle Ledger evidence. | SMERC returned `THROTTLE`, routed `CONSTRAINED_EXECUTE`, and assigned AWS reason codes EVIDENCE_INCOMPLETE, PRODUCTION_BLAST_RADIUS_WIDE, S3_POLICY_EXPOSURE. | The action can continue only through constrained execution such as scope limits, preview, checkpointing, or rate limits. Irreversible exposure score: 0.759. |
| Evaluate AWS-style `cloudformation` action `AWS_CFN_CHANGESET_REPLACE_005` before execution using hard evidence gates, recoverability scoring, Governance Routing Workbench routes, and Decision Lifecycle Ledger evidence. | SMERC returned `THROTTLE`, routed `CONSTRAINED_EXECUTE`, and assigned AWS reason codes CLOUDFORMATION_REPLACEMENT_RISK, PRODUCTION_BLAST_RADIUS_WIDE, ROLLBACK_UNCERTAIN. | The action can continue only through constrained execution such as scope limits, preview, checkpointing, or rate limits. Irreversible exposure score: 0.763. |
| Evaluate AWS-style `cloudformation` action `AWS_CFN_DRIFT_REMEDIATE_006` before execution using hard evidence gates, recoverability scoring, Governance Routing Workbench routes, and Decision Lifecycle Ledger evidence. | SMERC returned `DENY`, routed `BLOCK`, and assigned AWS reason codes AUTOMATED_REMEDIATION_PRESSURE, CLOUDFORMATION_REPLACEMENT_RISK, DRIFT_RECONCILIATION_RISK, EVIDENCE_INCOMPLETE, ROLLBACK_UNCERTAIN. | The action is blocked until the request is repaired, narrowed, or resubmitted with stronger evidence. Irreversible exposure score: 0.597. |
| Evaluate AWS-style `ecs` action `AWS_ECS_SCALE_SHIFT_007` before execution using hard evidence gates, recoverability scoring, Governance Routing Workbench routes, and Decision Lifecycle Ledger evidence. | SMERC returned `ALLOW`, routed `EXECUTE`, and assigned AWS reason codes ECS_CAPACITY_SHIFT. | The action is allowed with replay evidence because recovery and containment are strong enough for this metadata-only case. Irreversible exposure score: 0.31. |
| Evaluate AWS-style `rds` action `AWS_RDS_CLUSTER_DELETE_008` before execution using hard evidence gates, recoverability scoring, Governance Routing Workbench routes, and Decision Lifecycle Ledger evidence. | SMERC returned `DENY`, routed `BLOCK`, and assigned AWS reason codes EVIDENCE_INCOMPLETE, PRODUCTION_BLAST_RADIUS_WIDE, RDS_DATA_PLANE_RECOVERY_RISK, ROLLBACK_UNCERTAIN. | The action is blocked until the request is repaired, narrowed, or resubmitted with stronger evidence. Irreversible exposure score: 0.968. |

## Strategic Fit

Can AWS-style platform teams let agentic cloud automation move faster while still constraining actions that are authorized but not recoverable enough to execute now?

AWS-style controls can govern who may call a runtime, gateway, target, role, change set, or remediation path. SMERC adds a pre-execution judgment about rollback, containment, evidence, blast radius, cost velocity, and the route to ALLOW, THROTTLE, FREEZE, DENY, or ESCALATE.

Strongest first reviewers:
- AWS platform engineering teams
- cloud security architecture teams
- SRE and incident automation owners
- AI-agent platform teams
- FinOps and cloud cost automation owners
- infrastructure-as-code governance teams

Not claimed:
- AWS partnership
- AWS certification
- AWS production integration
- replacement for IAM, AgentCore Gateway, Bedrock Guardrails, CloudFormation, CloudTrail, CloudWatch, AWS Config, or human accountability

## Recommended Next Step

Ask an AWS-style reviewer to replace these examples with 5 to 25 metadata-only actions from one real workflow, then compare whether SMERC's recoverability posture changes their execution judgment.
