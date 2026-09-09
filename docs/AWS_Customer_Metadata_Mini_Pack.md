# AWS Customer Metadata Mini-Pack

## Purpose

This mini-pack is the shortest handoff from public AWS proof to reviewer-owned AWS-style metadata.

The ask is intentionally narrow:

> Replace the examples with 5 to 25 safe metadata-only AWS-style action summaries from one workflow, plus matching postcondition observation summaries if available.

Do not provide account IDs, ARNs, access keys, session tokens, secrets, raw CloudTrail events, raw CloudWatch logs, raw trace bodies, customer records, private topology, proprietary policy bodies, incident-sensitive details, or production commands.

## Files

- `examples/aws_bedrock_action_group_metadata_template.json`
- `examples/aws_cloud_platform_metadata_template.json`
- `examples/aws_postcondition_observation_template.json`
- `examples/aws_customer_metadata_filled_sample.json`
- `examples/aws_customer_postcondition_observations_sample.json`

## One-Command Reviewer Run

Run the public bundle with the filled sample:

```bash
python -m reference_engine.aws_reviewer_bundle \
  --customer-aws-source-exports examples/aws_customer_metadata_filled_sample.json \
  --customer-aws-observations examples/aws_customer_postcondition_observations_sample.json \
  --output-dir reports/aws_customer_mini_pack \
  --iterations 1 \
  --pretty
```

Generated customer-specific outputs:

- `reports/aws_customer_mini_pack/Customer_AWS_Metadata_Adapter_Report.md`
- `reports/aws_customer_mini_pack/customer_aws_metadata_adapter_report.json`
- `reports/aws_customer_mini_pack/customer_aws_normalized_customer_actions.json`
- `reports/aws_customer_mini_pack/customer_aws_customer_evaluation_report.json`
- `reports/aws_customer_mini_pack/Customer_AWS_Postcondition_Evidence_Report.md`
- `reports/aws_customer_mini_pack/customer_aws_postcondition_evidence_report.json`

## Work / Result / Impact

Work:

Ask a reviewer for safe AWS-style action summaries and optional postcondition observations from one workflow.

Result:

SMERC can normalize those summaries, score recoverability before execution, return posture and route controls, and compare expected controls against safe observation metadata.

Impact:

The AWS conversation moves from "interesting idea" to "can your team test this with five non-secret rows from one real workflow?"

## What The Sample Covers

- Bedrock-style Action Group / Lambda-backed tool invocation
- IAM execution-role permission expansion
- CloudFormation stateful change set
- S3 policy widening
- cost-velocity increase during retry-loop pressure

## What This Does Not Prove

- AWS endorsement
- AWS certification
- live AWS integration
- Marketplace listing
- production enforcement
- customer-validated incident reduction
- compliance attestation

## Best Next Reviewer Question

Can one AWS-style platform, cloud-security, SRE, FinOps, or agent-infrastructure reviewer replace this sample with 5 to 25 safe metadata-only actions from one owned workflow and say whether SMERC changed execution judgment?

