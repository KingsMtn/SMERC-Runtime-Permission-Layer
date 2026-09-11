# AWS Shadow Mirror Customer Metadata Request

## Purpose

This request is for an AWS-style reviewer who can provide sanitized mirror-derived summaries from one owned workflow.

The goal is to test whether SMERC can turn operational flow evidence into useful shadow-mode recoverability posture without packet payloads, live AWS access, account identifiers, credentials, raw logs, or private topology.

## The Ask

Please provide 5 to 25 sanitized mirror-derived summaries from one workflow using the shape in:

```text
examples/aws_shadow_mirror_customer_template.json
```

Good workflow families:

- agent runtime calling internal services
- agent runtime calling external APIs
- cloud automation worker egress
- sensitive data service egress
- remediation or rollback automation traffic
- gateway-controlled tool invocation traffic
- cost or scaling automation traffic

## Data Boundary

Do not send:

- packet payloads
- retained payload content
- raw packets
- raw flow logs
- raw CloudWatch logs
- AWS account IDs
- ARNs
- access keys
- session tokens
- secrets or credentials
- customer records
- private topology
- production commands
- live AWS access

Send only derived metadata such as source class, destination class, capture window, traffic velocity ratio, anomaly pressure, data sensitivity pressure, rollback availability, evidence quality, and current control outcome.

## Run

After replacing the template with customer-owned safe rows:

```bash
python -m reference_engine.aws_shadow_mirror_adapter customer_working/aws_shadow_mirror_rows.json \
  --normalized-output reports/customer_working/aws_shadow_mirror_normalized_customer_actions.json \
  --json-output reports/customer_working/aws_shadow_mirror_adapter_report.json \
  --markdown-output reports/customer_working/AWS_Shadow_Mirror_Adapter_Report.md \
  --customer-json-output reports/customer_working/aws_shadow_mirror_customer_evaluation_report.json \
  --customer-markdown-output reports/customer_working/AWS_Shadow_Mirror_Customer_Evaluation_Report.md \
  --pretty
```

## What SMERC Returns

- accepted rows
- skipped unsafe rows
- posture counts
- route states
- highest exposure flows
- high-velocity flow count
- sensitive-pattern flow count
- Decision Lifecycle Ledger evidence
- clear evidence boundary

## Work / Result / Impact

Work:

Ask for sanitized mirror-derived metadata from one AWS-style workflow and reject any payload-bearing or unsafe rows.

Result:

SMERC can compare operational flow evidence against recoverability posture in shadow mode.

Impact:

The AWS conversation moves closer to real-world proof because reviewers can test SMERC against operational behavior without granting access to live cloud systems or exposing sensitive data.

## Review Questions

- Did SMERC identify any currently allowed or alerted flow that should be throttled, frozen, denied, or escalated?
- Did SMERC catch high-velocity or high-sensitivity behavior current controls treat as routine?
- Were any rows skipped because the data boundary was unsafe?
- Would the posture have changed reviewer behavior during the captured workflow window?
- What evidence would make the posture more or less restrictive?

## What This Does Not Prove

- AWS endorsement
- AWS certification
- production firewall capability
- live AWS integration
- packet inspection
- incident reduction
- compliance attestation

This is a shadow-mode customer metadata request for recoverability-aware runtime governance.
