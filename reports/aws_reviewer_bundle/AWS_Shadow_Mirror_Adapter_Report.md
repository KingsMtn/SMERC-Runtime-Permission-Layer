# AWS Shadow Mirror Adapter Report

Generated: `2026-09-14T00:58:34+00:00`
Version: `smerc.aws-shadow-mirror-adapter.v1`

## Purpose

This report shows how SMERC can use sanitized AWS mirror-derived metadata as a shadow-mode evidence source.

It is not a firewall path. It is a safe observability path for testing recoverability posture before enforcement.

## Work / Result / Impact

- Work: Accept sanitized AWS mirror-derived flow summaries and reject unsafe rows before recoverability scoring.
- Result: Accepted 3 mirror summaries, skipped 1 unsafe or unsupported rows, and normalized accepted rows into the SMERC customer-evaluation contract.
- Impact: An AWS-style infrastructure reviewer can test SMERC against real operational flow metadata in shadow mode without exposing packet payloads, secrets, account identifiers, or live cloud access.

## Evidence Boundary

The adapter is a non-executing shadow-mode proof. It does not configure VPC Traffic Mirroring, attach ENIs, create NLB or Gateway Load Balancer targets, inspect packet payloads, retain payload content, call AWS APIs, assume roles, read live accounts, or enforce network policy.

## Adapter Intake

- Source export rows: `4`
- Accepted rows: `3`
- Skipped rows: `1`
- Mirror methods: `{'direct_eni_mirroring': 1, 'gateway_load_balancer_endpoint': 1, 'nlb_udp_fanout': 1}`
- Destination classes: `{'external_api': 1, 'internal_service': 1, 'internet_destination': 1}`
- High velocity accepted flows: `2`
- Sensitive-pattern accepted flows: `1`
- Skipped reason counts: `{'prohibited field present: raw_payload': 1}`

## Skipped Rows

| Record | Reason |
| --- | --- |
| `aws-mirror-004` | prohibited field present: raw_payload |

## SMERC Evaluation Summary

- Posture counts: `{'ALLOW': 1, 'DENY': 1, 'THROTTLE': 1}`
- Route counts: `{'BLOCK': 1, 'CONSTRAINED_EXECUTE': 1, 'EXECUTE': 1}`
- Ref-gate counts: `{'fail': 1, 'pass': 2}`
- Valid DLL ledgers: `3`
- Pilot fit: `moderate`

## Highest Exposure Accepted Flows

| Action | Posture | Route | Exposure |
| --- | --- | --- | ---: |
| `AWS_MIRROR_003_agent_workflow_attempts_high_volume_egress_from_sensitive_data_service_t` | `DENY` | `BLOCK` | 0.887 |
| `AWS_MIRROR_002_agent_automation_produces_elevated_outbound_traffic_to_an_external_api_c` | `THROTTLE` | `CONSTRAINED_EXECUTE` | 0.693 |
| `AWS_MIRROR_001_agent_runtime_calls_internal_customer_preference_service_through_governe` | `ALLOW` | `EXECUTE` | 0.222 |

## Reviewer Question

Can one AWS workflow export 5 to 25 sanitized mirror-derived summaries without payloads? If yes, SMERC can be evaluated in shadow mode before any enforcement discussion.
