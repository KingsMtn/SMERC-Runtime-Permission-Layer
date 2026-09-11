# AWS Pilot Request

## Purpose

This is the GitHub front door for an AWS-style SMERC pilot request.

It is intentionally metadata-only. A reviewer can test whether SMERC changes execution judgment without giving live AWS access, production logs, secrets, account identifiers, or customer data.

## What To Send

Send 5 to 25 safe AWS-style action summaries from one workflow.

Useful workflow lanes include:

- Bedrock Action Group / Lambda-backed tool action
- cloud platform automation
- IAM / Systems Manager / change execution
- CloudFormation / Terraform / infrastructure-as-code
- CloudWatch remediation / security response
- FinOps / cost-velocity automation
- S3 / data-access policy change
- cross-account delegation
- sanitized VPC Traffic Mirroring / NLB fan-out / Gateway Load Balancer endpoint summaries

For each action, include:

- action description
- actor or automated system
- target service or workflow family
- current outcome: `ALLOW`, `BLOCK`, `REVIEW`, or `UNKNOWN`
- why current controls produce that outcome
- possible consequence if the action is wrong
- rollback or recovery path
- optional postcondition observation showing whether the required route control happened

## What Not To Send

Do not send:

- account IDs
- ARNs
- access keys
- session tokens
- secrets or credentials
- raw CloudTrail events
- raw CloudWatch logs
- raw trace bodies
- customer records
- private topology
- proprietary policy bodies
- incident-sensitive details
- screenshots with identifiers
- production commands
- live AWS access

## What SMERC Returns

SMERC returns a metadata-only reviewer package:

- normalized accepted rows
- skipped or unsafe-row report
- recoverability posture for each action
- route controls
- reason codes
- evidence boundary
- optional postcondition evidence report
- readiness takeaways for bounded shadow-mode review

The posture vocabulary is:

- `ALLOW`
- `THROTTLE`
- `FREEZE`
- `DENY`
- `ESCALATE`

## One-Command Local Sample

Run the bundled sample:

```bash
python -m reference_engine.aws_reviewer_bundle \
  --customer-aws-source-exports examples/aws_customer_metadata_filled_sample.json \
  --customer-aws-observations examples/aws_customer_postcondition_observations_sample.json \
  --output-dir reports/aws_customer_mini_pack \
  --iterations 1 \
  --pretty
```

Inspect:

- `reports/aws_customer_mini_pack/AWS_Reviewer_Bundle.md`
- `reports/aws_customer_mini_pack/Customer_AWS_Metadata_Adapter_Report.md`
- `reports/aws_customer_mini_pack/Customer_AWS_Postcondition_Evidence_Report.md`

## GitHub Intake Path

Open an AWS metadata pilot request:

```text
https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/issues/new?template=aws_metadata_pilot_request.md
```

Use GitHub only for non-sensitive metadata. If the workflow cannot be safely described publicly, use the template as a checklist for a private technical review instead.

## Work / Result / Impact

Work:

Ask one AWS-style platform, cloud-security, SRE, FinOps, or agent-infrastructure reviewer for 5 to 25 non-secret action summaries from one owned workflow.

Result:

SMERC can compare current allow/block/review judgment against recoverability-aware posture and route controls before execution.

Impact:

The AWS conversation moves from abstract interest to a concrete question: would recoverability-aware pre-execution control change how a real workflow should be governed?

## What This Does Not Prove

- AWS endorsement
- AWS certification
- native AWS integration
- live Bedrock or AgentCore interception
- Marketplace listing
- production enforcement
- compliance attestation
- customer-validated incident reduction

## Best First Reviewer Question

Can SMERC identify one authorized AWS-style action that should be throttled, frozen, denied, or escalated because the action is not recoverable enough right now?
