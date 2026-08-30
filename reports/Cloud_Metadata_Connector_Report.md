# Cloud Metadata Connector Report

Generated: `2026-08-30T00:52:18+00:00`
Version: `smerc.cloud-metadata-connector.v1`

## Purpose

This report shows the practical bridge between a real company's cloud-change evidence and the SMERC runtime evaluation contract.

Instead of asking for credentials or live infrastructure access, the connector accepts read-only exported summaries and converts them into metadata-only SMERC actions.

## Work / Result / Impact

- Work: Convert safe cloud-change exports into strict SMERC customer-evaluation actions.
- Result: Generated 6 normalized actions and evaluated them through Ref-gates, recoverability scoring, SPARTa routing, autonomy budgeting, and DLL evidence.
- Impact: A company can test SMERC against familiar cloud-admin evidence before granting live access or building an enforcement integration.

## Evidence Boundary

The connector normalizes exported cloud-change summaries into SMERC metadata. It does not call AWS, Azure, Google Cloud, Cloudflare, Kubernetes, Terraform, DNS providers, databases, secrets managers, or production systems.

## Source Export Formats

| Source export format | Rows |
| --- | ---: |
| `backup_policy_change` | 1 |
| `cloudtrail_event_summary` | 1 |
| `dns_change_request` | 1 |
| `iam_access_analyzer_finding` | 1 |
| `kubernetes_rollout_plan` | 1 |
| `terraform_plan_change` | 1 |

## Current Controls vs SMERC Result

- Current control counts: `{'ALLOW': 4, 'REVIEW': 2}`
- SMERC posture counts: `{'DENY': 3, 'THROTTLE': 3}`
- SPARTa route counts: `{'BLOCK': 3, 'CONSTRAINED_EXECUTE': 3}`
- Ref-gate counts: `{'fail': 3, 'pass': 3}`
- Valid DLL ledgers: `6`
- Pilot fit: `strong`

## Highest Exposure Actions

| Action | Posture | Route | Exposure |
| --- | --- | --- | ---: |
| `CLOUD_EXPORT_003_delete_idle_database_cluster` | `DENY` | `BLOCK` | 0.964 |
| `CLOUD_EXPORT_006_shorten_backup_retention_after_cost_anomaly` | `DENY` | `BLOCK` | 0.827 |
| `CLOUD_EXPORT_001_expand_production_role_policy` | `DENY` | `BLOCK` | 0.763 |
| `CLOUD_EXPORT_002_widen_database_network_access` | `THROTTLE` | `CONSTRAINED_EXECUTE` | 0.705 |
| `CLOUD_EXPORT_005_cutover_production_dns_endpoint` | `THROTTLE` | `CONSTRAINED_EXECUTE` | 0.613 |

## Reviewer Question

Can this exported metadata be produced before the agent or automation executes the action? If yes, SMERC can run in shadow mode without live credentials.
