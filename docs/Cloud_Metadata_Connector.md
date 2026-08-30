# Cloud Metadata Connector

The Cloud Metadata Connector is the next practical step after the Cloud Admin Proof Pack.

It shows how a company could test SMERC without handing over live cloud credentials. A reviewer exports safe summaries from existing systems, then SMERC normalizes those summaries into the customer-evaluation contract.

## What It Accepts

Supported read-only export shapes:

- `iam_access_analyzer_finding`
- `terraform_plan_change`
- `cloudtrail_event_summary`
- `kubernetes_rollout_plan`
- `dns_change_request`
- `backup_policy_change`

These are representative export categories, not live vendor integrations.

## What It Produces

The connector produces:

- normalized `smerc.customer-evaluation.v1` action metadata
- Ref-gate results
- SMERC postures
- SPARTa routes
- Decision Lifecycle Ledger evidence
- autonomy-budget impact
- a markdown report for reviewers

## Run It

```bash
python -m reference_engine.cloud_metadata_connector examples/cloud_admin_source_exports.json --pretty
```

Default outputs:

- `examples/cloud_admin_normalized_customer_eval_actions.json`
- `reports/Cloud_Metadata_Connector_Report.md`
- `reports/cloud_metadata_connector_report.json`
- `reports/cloud_metadata_customer_evaluation/Customer_Evaluation_Report.md`
- `reports/cloud_metadata_customer_evaluation/customer_evaluation_report.json`

## Boundary

This connector does not call AWS, Azure, Google Cloud, Cloudflare, Kubernetes, Terraform, DNS providers, databases, secrets managers, or production systems.

It does not require:

- cloud credentials
- account identifiers
- private network details
- raw production logs
- source code
- secrets
- customer records
- live infrastructure commands

## Why It Matters

The Cloud Admin Proof Pack proves that SMERC can evaluate cloud-admin action metadata.

The Cloud Metadata Connector proves the safer intake path:

```text
existing cloud-change evidence
-> read-only exported summaries
-> normalized SMERC action metadata
-> SMERC posture
-> SPARTa route
-> Decision Lifecycle Ledger record
-> reviewer report
```

That is closer to how a real cloud, SRE, platform, DevOps, or AI-agent infrastructure team would test the system before any enforcement integration.

## Reviewer Question

Can your cloud or platform team produce safe pre-execution metadata for the actions your agents or automations are about to take?

If yes, SMERC can be tested in shadow mode before it touches production.
