# Tier 2 AWS Reviewer Front Door

## Purpose

This is the shortest GitHub-first path for a cloud, security, SRE, FinOps, or AI-infrastructure reviewer evaluating whether SMERC is worth testing with real AWS-style metadata.

The question is:

> Does recoverability before execution change cloud-agent or automation judgment enough to justify a bounded shadow-mode pilot?

For the shortest "why now" explanation, read `docs/Why_This_Matters_Now.md`.

## Start Here

Run:

```bash
python -m reference_engine.aws_reviewer_bundle --requested-actions 12 --pretty
```

Inspect:

- `reports/aws_reviewer_bundle/AWS_Reviewer_Bundle.md`
- `reports/aws_reviewer_bundle/AWS_Shadow_Mirror_Adapter_Report.md`
- `docs/AWS_Shadow_Mirror_Customer_Metadata_Request.md`
- `examples/aws_shadow_mirror_customer_template.json`
- `docs/Two_Tier_Valuation_Path.md`

## What SMERC Tests

SMERC tests whether an authorized action is recoverable enough to proceed right now.

It does not replace IAM, Bedrock guardrails, AgentCore Gateway, Cedar policies, CloudTrail, CloudWatch, Security Lake, SIEM, SOAR, approval workflows, or human accountability.

## What The AWS Tier 2 Package Includes

- AWS-style agent action-chain proof
- AWS metadata intake adapter
- AWS postcondition evidence
- AWS shadow mirror metadata evidence
- performance metrics
- customer-owned AWS metadata request
- customer-owned AWS shadow mirror template
- explicit no-payload and no-live-AWS boundary

## The Reviewer Ask

Provide one of these:

1. 5 to 25 safe AWS-style action summaries from one workflow.
2. 5 to 25 sanitized mirror-derived summaries from one workflow.
3. Both action summaries and matching postcondition observations.

Do not provide:

- AWS account IDs
- ARNs
- credentials
- raw logs
- packet payloads
- customer records
- private topology
- production commands
- live AWS access

## What SMERC Returns

- accepted rows
- skipped unsafe rows
- recoverability posture
- route controls
- evidence gaps
- highest exposure actions or flows
- performance observations
- Decision Lifecycle Ledger evidence
- pilot-fit next step

## Work / Result / Impact

Work:

Make the AWS-style Tier 2 proof path runnable and reviewable from GitHub while Netlify publishing is paused.

Result:

A reviewer can run the public bundle first, then replace examples with safe customer-owned metadata.

Impact:

SMERC moves from internal proof toward external market proof only when a reviewer labels whether the posture was useful, too strict, too loose, or irrelevant on real workflow metadata.

## Readiness Status

Current status:

> Ready for limited AWS-style technical review and customer-owned metadata replacement.

Not yet:

- production-ready
- AWS-certified
- AWS-endorsed
- independently security-audited
- proven to reduce incidents
- proven to have customer willingness to pay
- acquisition-grade Tier 3 evidence
