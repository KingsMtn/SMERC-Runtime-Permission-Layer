# AWS-Style Reviewer Bundle

## Purpose

The AWS-Style Reviewer Bundle gives a platform, cloud, or security reviewer one command that assembles the current SMERC AWS proof path.

It answers a practical question:

> If guardrails approve the content and IAM permits the actor, can SMERC still prove whether the action is recoverable enough to execute and whether the required route control happened afterward?

## Run

From the repository root:

```bash
python -m reference_engine.aws_reviewer_bundle --requested-actions 12 --pretty
```

Generated files:

```text
reports/aws_reviewer_bundle/AWS_Reviewer_Bundle.md
reports/aws_reviewer_bundle/aws_reviewer_bundle.json
reports/aws_reviewer_bundle/AWS_Agent_Action_Chain.md
reports/aws_reviewer_bundle/AWS_Agent_Action_Chain_Postcondition_Evidence.md
reports/aws_reviewer_bundle/AWS_Postcondition_Evidence_Report.md
reports/aws_reviewer_bundle/Serious_Report_Performance.md
reports/aws_reviewer_bundle/AWS_Customer_Owned_Metadata_Request.md
```

## What It Includes

- AWS Agent Action Chain proof.
- AWS Agent Action Chain Postcondition Evidence.
- AWS Postcondition Evidence using safe CloudTrail-, CloudWatch-, AgentCore-, MCP gateway-, and native change-record-shaped metadata.
- Serious report performance metrics.
- AWS customer-owned metadata request for 5 to 25 safe action and observation summaries.
- Readiness status and recommended next action.

## Reviewer Frame

Guardrails check content. IAM checks authority. SMERC checks recoverability. Postcondition evidence checks whether the route happened.

## Work / Result / Impact

Work: assemble the AWS-style proof path into one local package.

Result: the reviewer receives one report that summarizes AWS action-chain posture, route-control evidence, postcondition gaps, local p95 timing, metadata needs, and next action.

Impact: SMERC becomes easier for an AWS-style platform team to evaluate without founder-led explanation, live AWS access, raw logs, account IDs, ARNs, secrets, production commands, or execution authority.

## Evidence Boundary

This is a local, metadata-only AWS-style review package. It does not connect to AWS, invoke Amazon Bedrock, call IAM, run Systems Manager, apply CloudFormation, read CloudTrail or CloudWatch, modify infrastructure, prove AWS endorsement, prove AWS certification, or establish production safety.

## Next Proof

The next real proof is external: a reviewer replaces the examples with 10 to 25 safe AWS-style metadata actions and matching observation summaries from one owned workflow, then decides whether recoverability before execution changes their review judgment enough to justify shadow-mode testing.
