# AWS Cloud Action Replay

## Purpose

AWS Cloud Action Replay gives platform, cloud-security, SRE, FinOps, and AI-agent reviewers a focused way to test SMERC against AWS-style automation decisions.

It uses metadata-only examples for:

- Amazon Bedrock AgentCore-style runtime and gateway actions
- IAM role and permission changes
- S3 bucket-policy exposure
- CloudFormation change sets
- drift-aware remediation
- ECS/Fargate-style capacity movement
- RDS cluster administration
- CloudWatch-style automated remediation
- spend-velocity growth
- Secrets Manager-style rotation
- cross-account delegation

## Why This Matters

AWS already has strong control surfaces for identity, gateway enforcement, guardrails, monitoring, logging, and infrastructure change management.

SMERC should not pretend to replace those systems. The AWS-fit question is more specific:

```text
After normal authorization says an action can be attempted,
is this specific action recoverable, bounded, evidenced,
and safe to proceed right now?
```

That question matters for agentic cloud automation because an authorized tool call can still have weak rollback, wide blast radius, incomplete evidence, high cost velocity, or ambiguous ownership.

## Work / Result / Impact

Work:

Run twelve AWS-style metadata actions through SMERC's customer-evaluation contract, hard evidence gates, recoverability scoring, Governance Routing Workbench routes, autonomy budgeting, and Decision Lifecycle Ledger proof.

Result:

The generated report returns posture counts, route counts, AWS reason codes, AWS-style surface counts, valid ledger counts, and reviewer-readable Work / Result / Impact examples.

Impact:

A reviewer can see where an AWS-style action should be allowed, throttled, frozen, denied, or escalated before side effects occur. This turns the AWS conversation into runnable proof instead of a claim.

## Run

```bash
python -m reference_engine.aws_cloud_action_replay --pretty
```

Outputs:

```text
reports/aws_cloud_action_replay/AWS_Cloud_Action_Replay.md
reports/aws_cloud_action_replay/aws_cloud_action_replay.json
```

## Reason Codes

The report adds AWS-style reason codes including:

- `AGENTCORE_TOOL_SIDE_EFFECT`
- `AGENTCORE_GATEWAY_BYPASS_RISK`
- `IAM_SCOPE_EXPANSION`
- `S3_POLICY_EXPOSURE`
- `CLOUDFORMATION_REPLACEMENT_RISK`
- `DRIFT_RECONCILIATION_RISK`
- `ECS_CAPACITY_SHIFT`
- `RDS_DATA_PLANE_RECOVERY_RISK`
- `AUTOMATED_REMEDIATION_PRESSURE`
- `COST_VELOCITY_SPIKE`
- `SECRETS_ROTATION_IMPACT`
- `CROSS_ACCOUNT_DELEGATION_RISK`
- `ROLLBACK_UNCERTAIN`
- `EVIDENCE_INCOMPLETE`
- `PRODUCTION_BLAST_RADIUS_WIDE`

## Boundary

This is AWS-style metadata-only proof. It does not connect to AWS, invoke AgentCore, read CloudTrail, inspect CloudFormation stacks, call IAM, access S3, change RDS, execute CloudWatch remediation, rotate credentials, move funds, create infrastructure, or use customer telemetry.

It is not AWS endorsement, AWS certification, production-readiness proof, compliance evidence, or incident-reduction proof.

## Customer Next Step

The best external test is:

```text
one AWS-style workflow family -> 5 to 25 metadata-only customer actions -> SMERC replay -> reviewer labels -> shadow-mode pilot decision
```

Good first workflow families:

- agent runtime tool invocation
- AgentCore Gateway-style policy bypass prevention
- IAM execution-role changes
- CloudFormation change-set execution
- drift remediation
- database cleanup
- CloudWatch automated remediation
- cloud cost automation
- cross-account delegation
