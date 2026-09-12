# SMERC v0.15 AWS Tier 2 Review Notes

## Purpose

This release note summarizes the AWS-style Tier 2 proof path added for reviewers while Netlify publishing is paused.

It is meant for GitHub, AI search, and technical reviewers who need the shortest dated summary of what changed.

## Summary

SMERC now has a stronger AWS-style reviewer path for testing pre-execution recoverability control against cloud-agent actions and sanitized operational metadata.

The new proof path is still metadata-only. It does not require AWS credentials, account IDs, ARNs, packet payloads, raw logs, customer records, private topology, production commands, or live AWS access.

## What Changed

- Added AWS shadow mirror metadata support for sanitized VPC Traffic Mirroring, Network Load Balancer fan-out, and Gateway Load Balancer endpoint summaries.
- Added a customer-owned AWS shadow mirror metadata request for 5 to 25 sanitized mirror-derived summaries from one workflow.
- Added a GitHub issue template for AWS shadow mirror metadata requests.
- Integrated AWS shadow mirror evidence into the one-command AWS reviewer bundle.
- Added the two-tier valuation path separating the public decision-language layer from the enterprise cloud-action governance package.
- Added an implementer quickstart and emitter path for outside frameworks to emit `smerc.decision.v1`.

## Work / Result / Impact

Work:

Make GitHub carry the current public proof path while Netlify deployment is paused.

Result:

AWS-style reviewers can now run one local bundle that includes action-chain proof, AWS postcondition evidence, shadow mirror metadata evidence, performance metrics, and customer-owned metadata requests.

Impact:

SMERC is closer to a Tier 2 technical review package because it can evaluate both proposed cloud actions and observed operational flow metadata in shadow mode without asking for sensitive data or live cloud access.

## Best Reviewer Path

Run:

```bash
python -m reference_engine.aws_reviewer_bundle --requested-actions 12 --pretty
```

Then inspect:

- `reports/aws_reviewer_bundle/AWS_Reviewer_Bundle.md`
- `reports/aws_reviewer_bundle/AWS_Shadow_Mirror_Adapter_Report.md`
- `docs/AWS_Shadow_Mirror_Customer_Metadata_Request.md`
- `examples/aws_shadow_mirror_customer_template.json`
- `docs/Two_Tier_Valuation_Path.md`

## What This Proves

- SMERC can assemble AWS-style proof in one command.
- SMERC can reject unsafe mirror rows that include payload-like data.
- SMERC can return `ALLOW`, `THROTTLE`, and `DENY` outcomes from sanitized operational metadata.
- SMERC can preserve an explicit evidence boundary for AWS-style review.

## What This Does Not Prove

- AWS endorsement
- AWS certification
- production deployment readiness
- production firewall capability
- live incident reduction
- customer willingness to pay
- acquisition value

## Evidence Still Needed

The next Tier 2 proof is external:

> A reviewer replaces the examples with 5 to 25 safe AWS-style action or mirror-derived metadata rows from one owned workflow and labels whether SMERC's posture was useful, too strict, too loose, or irrelevant.

That is the step that moves SMERC from internal proof toward market proof.
