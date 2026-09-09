# SMERC Serious Report Performance

Generated: `2026-09-09T07:58:12+00:00`
Version: `smerc.serious-report-performance.v1`
Iterations per workload: `1`
Status: `ready_for_local_review`

## Work / Result / Impact

- Work: Run serious SMERC proof paths repeatedly and summarize local execution latency.
- Result: Measured 4 proof workloads across 1 iteration(s) each with slowest p95 of 7.333 ms.
- Impact: Reviewers can see whether proof generation is lightweight enough for local evaluation, while customer pilots still measure production p50, p95, workflow overhead, and reviewer impact.

## Evidence Boundary

This is local reference performance evidence for report builders. It does not prove production latency, hosted API performance, customer workflow overhead, reviewer burden, throughput, SLA, or enforcement-path performance.

## Workloads

| Workload | Runs | p50 ms | p95 ms | Max ms | Result facts |
| --- | ---: | ---: | ---: | ---: | --- |
| `customer_evaluation_general` | 1 | 5.437 | 5.437 | 5.437 | actions=5, valid_ledgers=5, postures={'ALLOW': 1, 'DENY': 3, 'THROTTLE': 1} |
| `cloud_metadata_connector` | 1 | 7.333 | 7.333 | 7.333 | actions=6, valid_ledgers=6, postures={'DENY': 3, 'THROTTLE': 3} |
| `public_benchmark_ingestion` | 1 | 6.671 | 6.671 | 6.671 | actions=10, valid_ledgers=10, postures={'ALLOW': 2, 'DENY': 6, 'THROTTLE': 2} |
| `postcondition_evidence` | 1 | 6.195 | 6.195 | 6.195 | actions=10, observed=5, statuses={'gap': 1, 'pass': 4, 'unobserved': 5} |

## Reviewer Question

Which proof path should be timed inside a customer workflow, and what p95 overhead would make the integration unacceptable?
