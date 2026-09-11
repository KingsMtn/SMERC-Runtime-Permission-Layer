# AWS Shadow Mirror Metadata Path

## Purpose

This path captures the useful part of AWS VPC Traffic Mirroring, Network Load Balancer fan-out, and Gateway Load Balancer endpoint patterns without turning SMERC into a packet firewall.

SMERC should use mirror-derived metadata as a shadow-mode evidence source. It should not ingest packet payloads, secrets, account identifiers, raw logs, private topology, or live AWS access during public review.

## Work / Result / Impact

Work:

Normalize sanitized AWS mirror-derived flow summaries into the SMERC customer-evaluation contract.

Result:

SMERC can score operational flow evidence from direct ENI mirroring, NLB UDP fan-out, or Gateway Load Balancer endpoint summaries and return recoverability posture, route state, controls, and Decision Lifecycle Ledger evidence.

Impact:

An AWS-style reviewer can test SMERC against realistic operational behavior in shadow mode before any enforcement, marketplace, or live cloud integration discussion.

## Where It Fits

```text
AWS agent or automation activity
-> Bedrock or gateway/content guardrail
-> IAM and policy authorization
-> VPC Traffic Mirroring, NLB fan-out, or Gateway Load Balancer endpoint summary
-> sanitized metadata extractor
-> SMERC shadow mirror adapter
-> recoverability posture and route evidence
-> postcondition evidence and reviewer labels
```

This placement is intentionally observe-only. Existing AWS and customer controls remain authoritative.

## Supported Mirror-Derived Sources

- `vpc_traffic_mirror_eni_summary`
- `nlb_udp_fanout_summary`
- `gateway_load_balancer_endpoint_summary`

These are not raw AWS exports. They are sanitized summaries produced by a customer-controlled extractor.

## Required Boundary

Accepted rows must be metadata-only.

Allowed examples:

- source service class
- destination class
- capture window
- traffic velocity ratio
- anomaly pressure
- data sensitivity pressure
- sensitive-pattern indicator
- rollback path availability
- containment estimate
- evidence quality
- current control posture

Rejected examples:

- packet payloads
- retained payload content
- raw packets
- raw logs
- account IDs
- ARNs
- credentials
- customer records
- private topology
- production commands
- live AWS access

Rows containing prohibited fields or payload retention are skipped.

## Run

```bash
python -m reference_engine.aws_shadow_mirror_adapter examples/aws_shadow_mirror_source_exports.json --pretty
```

Outputs:

```text
examples/aws_shadow_mirror_normalized_customer_eval_actions.json
reports/aws_shadow_mirror/AWS_Shadow_Mirror_Adapter_Report.md
reports/aws_shadow_mirror/aws_shadow_mirror_adapter_report.json
reports/aws_shadow_mirror/Customer_Evaluation_Report.md
reports/aws_shadow_mirror/customer_evaluation_report.json
```

## Customer-Owned Metadata Request

When a reviewer is ready to use their own data, use:

- `docs/AWS_Shadow_Mirror_Customer_Metadata_Request.md`
- `examples/aws_shadow_mirror_customer_template.json`
- `.github/ISSUE_TEMPLATE/aws_shadow_mirror_metadata_request.md`

The request stays narrow: 5 to 25 sanitized mirror-derived summaries from one workflow, no payloads, no raw logs, no identifiers, no credentials, and no live AWS access.

## Reviewer Question

Can one AWS workflow export 5 to 25 sanitized mirror-derived summaries without payloads?

If yes, SMERC can be tested in shadow mode against real operational flow behavior before anyone trusts it to enforce.

## Non-Claims

This path does not claim:

- AWS partnership
- AWS endorsement
- AWS certification
- production firewall capability
- live AWS integration
- incident prevention
- packet inspection
- compliance attestation

It is a metadata-only shadow-mode evidence path for recoverability-aware runtime governance.
