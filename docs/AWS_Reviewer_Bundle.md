# AWS-Style Reviewer Bundle

## Purpose

The AWS-Style Reviewer Bundle gives a platform, cloud, or security reviewer one command that assembles the current SMERC AWS proof path.

It answers a practical question:

> If guardrails approve the content and IAM permits the actor, can SMERC still prove whether the action is recoverable enough to execute and whether the required route control happened afterward?

For AWS-style platform teams, the commercial translation is sharper: can SMERC reduce systemic liability and downtime risk for autonomous cloud execution without slowing every authorized action into manual review?

## Run

From the repository root:

```bash
python -m reference_engine.aws_reviewer_bundle --requested-actions 12 --pretty
```

For the shortest reviewer path, start with `docs/AWS_Reviewer_Quickstart.md`.

Generated files:

```text
reports/aws_reviewer_bundle/AWS_Reviewer_Bundle.md
reports/aws_reviewer_bundle/aws_reviewer_bundle.json
reports/aws_reviewer_bundle/AWS_Agent_Action_Chain.md
reports/aws_reviewer_bundle/AWS_Decision_API_Surface.md
reports/aws_reviewer_bundle/sample_decision_request.json
reports/aws_reviewer_bundle/sample_decision_response.json
reports/aws_reviewer_bundle/AWS_Agent_Action_Chain_Postcondition_Evidence.md
reports/aws_reviewer_bundle/AWS_Postcondition_Evidence_Report.md
reports/aws_reviewer_bundle/AWS_Shadow_Mirror_Adapter_Report.md
reports/aws_reviewer_bundle/Serious_Report_Performance.md
reports/aws_reviewer_bundle/AWS_Customer_Owned_Metadata_Request.md
```

## What It Includes

- AWS Agent Action Chain proof.
- AWS Decision API Surface at `docs/AWS_Decision_API_Surface.md`, with OpenAPI operation ID `evaluateAwsActionRecoverability`.
- Lambda-shaped Bedrock Agent Action Group decision-handler pattern at `docs/AWS_Bedrock_Agent_Kill_Switch_Pattern.md`.
- AWS Customer Metadata Mini-Pack at `docs/AWS_Customer_Metadata_Mini_Pack.md`.
- AWS Agent Action Chain Postcondition Evidence.
- AWS Security Ecosystem Evidence Path at `docs/AWS_Security_Ecosystem_Evidence_Path.md`.
- AWS Postcondition Evidence using safe CloudTrail-, CloudWatch-, AgentCore-, MCP gateway-, and native change-record-shaped metadata.
- AWS Shadow Mirror Metadata Path using sanitized VPC Traffic Mirroring, NLB fan-out, or Gateway Load Balancer endpoint summaries without packet payloads.
- Serious report performance metrics.
- AWS customer-owned metadata request for 5 to 25 safe action and observation summaries.
- Customer-owned AWS metadata template at `examples/aws_customer_metadata_template.json`.
- Customer-owned AWS shadow mirror template at `examples/aws_shadow_mirror_customer_template.json`.
- AWS Marketplace Validation Path at `docs/AWS_Marketplace_Validation_Path.md`.
- Defensible Moat and Commercial Boundary at `docs/SMERC_Defensible_Moat_And_Commercial_Boundary.md`.
- Readiness status and recommended next action.

## Reviewer Frame

Guardrails check content. IAM checks authority. SMERC checks recoverability. Shadow mirror metadata tests operational behavior. Postcondition evidence checks whether the route happened. AWS security evidence systems can receive posture and route facts after the decision, but they do not replace the pre-execution recoverability question.

## Work / Result / Impact

Work: assemble the AWS-style proof path into one local package.

Result: the reviewer receives one report that summarizes AWS action-chain posture, a Lambda/OpenAPI decision surface, shadow-mirror operational evidence, route-control evidence, postcondition gaps, local p95 timing, metadata needs, and next action.

Impact: SMERC becomes easier for an AWS-style platform team to evaluate without founder-led explanation, live AWS access, raw logs, account IDs, ARNs, secrets, production commands, or execution authority.

## Evidence Boundary

This is a local, metadata-only AWS-style review package. It does not connect to AWS, invoke Amazon Bedrock, call IAM, run Systems Manager, apply CloudFormation, read CloudTrail or CloudWatch, configure VPC Traffic Mirroring, inspect packet payloads, publish to Security Lake, create EventBridge rules, list on AWS Marketplace, modify infrastructure, prove AWS endorsement, prove AWS certification, or establish production safety.

## Next Proof

The next real proof is external: a reviewer replaces the examples with 10 to 25 safe AWS-style metadata actions and matching observation summaries from one owned workflow, then decides whether recoverability before execution changes their review judgment enough to justify shadow-mode testing.

Use `examples/aws_customer_metadata_template.json` as the starting shape for that replacement.

Use `examples/aws_shadow_mirror_customer_template.json` if the reviewer wants to test sanitized mirror-derived operational summaries.

For a runnable sample of that handoff, use:

```bash
python -m reference_engine.aws_reviewer_bundle \
  --customer-aws-source-exports examples/aws_customer_metadata_filled_sample.json \
  --customer-aws-observations examples/aws_customer_postcondition_observations_sample.json \
  --output-dir reports/aws_customer_mini_pack \
  --iterations 1 \
  --pretty
```
