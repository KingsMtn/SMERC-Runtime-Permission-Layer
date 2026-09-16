---
name: AWS metadata pilot request
about: Submit a metadata-only AWS-style workflow for SMERC recoverability review
title: "AWS metadata pilot: "
labels: ["pilot-intake", "customer-evaluation", "aws-review"]
---

## Data Boundary

Do not include account IDs, ARNs, access keys, session tokens, secrets, credentials, raw CloudTrail events, raw CloudWatch logs, raw traces, customer records, private topology, proprietary policy bodies, incident-sensitive details, screenshots with identifiers, or production commands.

Use safe metadata only.

## Reviewer Perspective

Examples: AWS platform engineer, cloud security architect, SRE, FinOps lead, AI infrastructure owner, agent-runtime reviewer, security automation owner.

## Workflow Lane

Choose one:

- Bedrock Action Group / Lambda-backed tool action
- cloud platform automation
- IAM / Systems Manager / change execution
- CloudFormation / Terraform / infrastructure-as-code
- CloudWatch remediation / security response
- FinOps / cost-velocity automation
- S3 / data-access policy change
- cross-account delegation
- other

## Current Controls

What currently decides whether the action proceeds?

Examples: IAM, approval ticket, change window, Bedrock-style guardrail, AI gateway, OPA/policy-as-code, manual review, runbook, CloudFormation review, CI/CD approval, security playbook, mixed controls, not clearly defined.

## Action Examples

Provide 5 to 25 metadata-only AWS-style actions from one workflow. For each action, include:

- action description
- actor or automated system
- target service or workflow family
- current outcome: `ALLOW`, `BLOCK`, `REVIEW`, or `UNKNOWN`
- why current controls produce that outcome
- possible consequence if the action is wrong
- rollback or recovery path
- environment boundary if known: tooling isolation, host isolation, network isolation, sandbox escape surfaces, execution boundary
- whether a route control was observed after the decision, if known

Example:

```text
Action 1:
Description: Agent requests a CloudFormation change set for an autoscaling policy update.
Actor/system: cloud_ops_agent through approved workflow
Target service: CloudFormation / Auto Scaling
Current outcome: ALLOW
Current reason: IAM role and change ticket are valid
Possible consequence: rapid over-scaling or service instability
Rollback path: revert change set or restore previous scaling policy within 20 minutes
Environment boundary: CI runner, container host isolation, production network access, no known sandbox escape surface
Observed route control: change set review required before execution
```

## Review Question

What should SMERC help answer?

Examples:

- Should authorized agent actions still be throttled, frozen, denied, or escalated before execution?
- Are rollback latency and blast radius visible enough before the action runs?
- Do current controls miss cost velocity, containment, fallback, or postcondition evidence?
- Would SMERC create a useful middle state between allow and block?

## What Would Make This Worth A Pilot?

Examples:

- SMERC identifies actions current controls allow but reviewers would want constrained.
- SMERC detects missing evidence before recoverability scoring.
- SMERC produces useful disagreement with current allow/block decisions.
- SMERC gives clearer route controls and postcondition evidence.
- SMERC distinguishes authority from recoverability.

## Preferred Next Step

Choose one:

- public GitHub discussion
- private follow-up outside GitHub
- run the sample mini-pack locally first
- technical review only
- shadow-mode AWS metadata pilot discussion

## Relevant Links

- External metadata reviewer request: https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/docs/External_Metadata_Reviewer_Request.md
- Tier 2 AWS reviewer front door: https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/docs/Tier2_AWS_Reviewer_Front_Door.md
- AWS pilot front door: https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/docs/AWS_PILOT_REQUEST.md
- AWS customer metadata mini-pack: https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/docs/AWS_Customer_Metadata_Mini_Pack.md
- AWS reviewer quickstart: https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/docs/AWS_Reviewer_Quickstart.md
- Filled AWS sample: https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/examples/aws_customer_metadata_filled_sample.json
- Sample AWS mini-pack report: https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/reports/aws_customer_mini_pack/AWS_Reviewer_Bundle.md
