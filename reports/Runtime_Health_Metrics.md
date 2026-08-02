# SMERC Runtime Health Metrics

Generated: `2026-08-02T03:25:14+00:00`

## Status

- Tenant: `pilot-review`
- Health status: `healthy`

## Decision Volume

- Decisions: `10`
- Observed evaluations: `10`
- Posture counts: `{'ALLOW': 2, 'THROTTLE': 3, 'FREEZE': 1, 'DENY': 0, 'ESCALATE': 4, 'UNAVAILABLE': 0}`

## Latency

- SLO: `250 ms p95`
- Sample count: `10`
- Average: `31.6` ms
- p50: `33.0` ms
- p95: `44.2` ms
- p99: `45.64` ms
- Maximum: `46.0` ms
- SLO met: `True`

## Resilience

- Integration status counts: `{'ok': 10}`
- Unavailable count: `0`
- Unavailable rate: `0.0`
- Fail-closed count: `0`
- Fail-closed rate: `0.0`

## Operational Checks

| Check | Status | Detail |
| --- | --- | --- |
| `observations_present` | `ready` | Runtime health requires evaluation observations; without them, latency and availability are unknown. |
| `latency_p95` | `ready` | p95 evaluation latency should remain at or below 250 ms for the selected workflow. |
| `unavailable_rate` | `ready` | Unavailable rate warning threshold is 0.01; blocker threshold is 0.05. |
| `evidence_status_labeled` | `ready` | Observation source must be labeled before using the report externally. |

## Evidence Boundary

Runtime health metrics summarize supplied decision artifacts and observation records. Reference/local observations do not prove customer production latency, availability, incident reduction, or SLA compliance.
