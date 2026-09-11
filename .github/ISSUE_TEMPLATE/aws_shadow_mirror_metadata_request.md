---
name: AWS shadow mirror metadata request
about: Submit sanitized mirror-derived AWS flow summaries for SMERC shadow-mode review
title: "AWS shadow mirror metadata: "
labels: ["pilot-intake", "customer-evaluation", "aws-review", "shadow-mode"]
---

## Data Boundary

Do not include packet payloads, retained payload content, raw packets, raw flow logs, raw CloudWatch logs, account IDs, ARNs, access keys, session tokens, secrets, credentials, customer records, private topology, incident-sensitive details, screenshots with identifiers, production commands, or live AWS access.

Use safe derived metadata only.

## Reviewer Perspective

Examples: AWS platform engineer, cloud security architect, SRE, network security reviewer, AI infrastructure owner, agent-runtime reviewer.

## Mirror-Derived Source

Choose one:

- VPC Traffic Mirroring direct ENI summary
- Network Load Balancer fan-out summary
- Gateway Load Balancer endpoint summary
- other sanitized flow-summary source

## Workflow Lane

Choose one:

- agent runtime calling internal services
- agent runtime calling external APIs
- cloud automation worker egress
- sensitive data service egress
- remediation or rollback automation traffic
- gateway-controlled tool invocation traffic
- cost or scaling automation traffic
- other

## Current Controls

What currently observes or decides whether the flow is acceptable?

Examples: IAM, network firewall, VPC endpoint policy, gateway policy, SIEM alert, CloudWatch alarm, approval workflow, manual review, runbook, AI gateway, not clearly defined.

## Mirror Metadata Examples

Provide 5 to 25 sanitized mirror-derived rows from one workflow. For each row, include:

- non-sensitive observed flow summary
- source service class
- destination class
- capture window
- traffic velocity ratio
- anomaly pressure
- data sensitivity pressure
- rollback path availability
- current outcome: `ALLOW`, `BLOCK`, `REVIEW`, `ALERT`, or `UNKNOWN`
- whether any sensitive-pattern indicator was present, without including the payload

Example:

```text
Flow 1:
Observed flow: Agent runtime calls internal preference service through governed endpoint.
Source class: agent_runtime
Destination class: internal_service
Capture window: five-minute summary
Current outcome: ALLOW
Traffic velocity: low
Anomaly pressure: low
Data sensitivity pressure: medium
Rollback path: available
Sensitive-pattern indicator: false
Payload included: no
```

## Review Question

What should SMERC help answer?

Examples:

- Should mirrored operational behavior affect pre-execution posture?
- Are high-velocity or high-sensitivity flows visible before an agent continues?
- Would SMERC create a useful middle state between alert and block?
- Does the current workflow distinguish authorization from recoverability?

## Preferred Next Step

Choose one:

- public GitHub discussion
- private follow-up outside GitHub
- run the sample shadow mirror adapter locally first
- technical review only
- shadow-mode AWS mirror metadata pilot discussion

## Relevant Links

- AWS shadow mirror metadata path: https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/docs/AWS_Shadow_Mirror_Metadata_Path.md
- AWS shadow mirror customer request: https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/docs/AWS_Shadow_Mirror_Customer_Metadata_Request.md
- Shadow mirror template: https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/examples/aws_shadow_mirror_customer_template.json
- Sample shadow mirror report: https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/reports/aws_shadow_mirror/AWS_Shadow_Mirror_Adapter_Report.md
