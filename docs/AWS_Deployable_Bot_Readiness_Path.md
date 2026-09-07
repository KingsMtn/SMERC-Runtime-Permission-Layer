# AWS Deployable Bot Readiness Path

## Purpose

This path defines what SMERC should prove if the long-term target is an AWS-style platform team deploying SMERC as a governed action bot for agentic cloud automation.

The goal is not to claim AWS partnership, AWS endorsement, AWS certification, or AWS production integration. The goal is to make SMERC credible enough that an AWS-style reviewer can see exactly where it would fit, what it would need to consume, what it would return, and what evidence it would preserve.

## Target Shape

SMERC should behave like a recoverability-aware action bot that sits between agentic automation and consequential cloud actions.

Input:

- proposed agent action
- actor and workload identity
- tool or API target
- requested scope
- trusted evidence
- rollback and cancellation facts
- blast-radius estimate
- cost-velocity estimate
- current autonomy budget
- postcondition evidence expectations

Output:

- `ALLOW`
- `THROTTLE`
- `FREEZE`
- `DENY`
- `ESCALATE`
- reason codes
- required controls
- Governance Routing Workbench route
- Decision Lifecycle Ledger evidence
- reviewer-ready Work / Result / Impact report

## Work / Result / Impact

Work:

Build SMERC toward an AWS-style deployable bot shape by proving safe metadata ingestion, hard evidence gates, recoverability scoring, route generation, control evidence, autonomy budgeting, and audit replay for cloud and agent actions.

Result:

A reviewer can run public examples first, then replace them with 5 to 25 metadata-only actions from one real AWS-style workflow.

Impact:

The project becomes easier to evaluate as infrastructure that could complement cloud identity, gateway, guardrail, logging, monitoring, change-management, and approval systems rather than a loose security idea.

## Readiness Milestones

### 1. Public AWS-Style Replay

Status: started.

Current artifact:

```bash
python -m reference_engine.aws_cloud_action_replay --pretty
```

This proves AWS-style metadata can move through the SMERC customer-evaluation contract with reason codes, posture counts, route evidence, autonomy budget impact, and DLL validity.

### 2. AWS Metadata Intake Contract

Next build.

Create a strict metadata contract for AWS-style evidence:

- agent runtime target
- gateway or direct-runtime path
- IAM role or policy change summary
- CloudFormation change-set summary
- drift-detection summary
- CloudTrail-style action summary
- CloudWatch alarm/remediation summary
- RDS snapshot or deletion summary
- S3 policy exposure summary
- cost-velocity estimate
- Secrets Manager rotation summary
- cross-account trust summary

Boundary:

No live AWS credentials, account IDs, ARNs, secrets, private topology, production logs, or customer records should be required for public review.

### 3. AWS Adapter Stub

Build a non-executing adapter that accepts read-only exported summaries and normalizes them into SMERC actions.

It should not call AWS APIs by default.

It should produce:

- accepted rows
- skipped rows
- skipped reasons
- SMERC action metadata
- source version
- evidence boundary

### 4. Postcondition Evidence For Cloud Controls

Extend postcondition evidence to AWS-style controls:

- dry-run or preview observed
- scope limit applied
- checkpoint recorded
- rollback plan attached
- approval route created
- gateway path enforced
- direct runtime path rejected
- execution blocked
- replay preserved

This matters because reviewers need to see whether SMERC only recommended a control or whether an adapter supplied evidence that the control happened.

### 5. Performance And Overhead Report

Add AWS replay timing to serious performance reports.

Measure:

- local decision latency
- route-generation latency
- report-generation latency
- p50
- p95
- maximum observed time
- evidence boundary

Do not claim production SLA until tested inside a real environment.

### 6. Customer-Owned AWS Metadata Request

Create a reviewer ask:

```text
Please replace the public examples with 5 to 25 metadata-only actions from one AWS-style workflow.
Do not include secrets, credentials, account IDs, ARNs, raw logs, customer records, private topology, or production commands.
```

Good first workflows:

- agent runtime tool calls
- gateway-controlled tool invocation
- IAM execution-role changes
- CloudFormation change-set execution
- drift remediation
- RDS cleanup or restore path
- S3 access-policy changes
- CloudWatch automated remediation
- cloud cost automation
- cross-account delegation

### 7. Shadow-Mode Pilot Shape

If metadata review is useful, the next stage is shadow mode:

- SMERC observes proposed actions.
- Existing AWS/customer controls remain authoritative.
- SMERC records the posture it would have returned.
- Reviewers label whether the posture was useful, too strict, too loose, or irrelevant.
- No production enforcement happens without a separate written agreement.

## Success Criteria

SMERC is closer to an AWS-deployable bot when it can show:

- one-command public replay
- clean metadata intake
- no secrets required
- clear AWS-style reason codes
- useful posture differences
- postcondition evidence
- performance overhead
- customer-owned metadata path
- bounded shadow-mode pilot plan
- clear commercial-use boundary

## Non-Claims

This path does not claim:

- AWS partnership
- AWS endorsement
- AWS certification
- live AWS integration
- production safety
- compliance support
- incident reduction
- customer willingness to pay
- replacement for IAM, AgentCore Gateway, Bedrock Guardrails, CloudFormation, CloudTrail, CloudWatch, AWS Config, or human accountability

## Commercial Boundary

Public review, research, non-production evaluation, and metadata-only pilot testing are governed by the `SMERC Public Review License v1.0`.

Production deployment, commercial embedding, hosted use, resale, revenue-generating use, or integration into a commercial product, internal enterprise platform, cloud service, agent framework, financial workflow, security product, or managed service requires a separate written commercial license or agreement.

Organizations evaluating acquisition, strategic partnership, or production use should contact the project owner before implementation.
