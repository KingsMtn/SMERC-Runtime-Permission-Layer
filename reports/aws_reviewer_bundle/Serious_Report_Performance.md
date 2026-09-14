# SMERC Serious Report Performance

Generated: `2026-09-14T00:58:34+00:00`
Version: `smerc.serious-report-performance.v1`
Iterations per workload: `5`
Status: `ready_for_local_review`

## Work / Result / Impact

- Work: Run serious SMERC proof paths repeatedly and summarize local execution latency.
- Result: Measured 4 proof workloads across 5 iteration(s) each with slowest p95 of 8.584 ms.
- Impact: Reviewers can see whether proof generation is lightweight enough for local evaluation, while customer pilots still measure production p50, p95, workflow overhead, and reviewer impact.

## Evidence Boundary

This is local reference performance evidence for report builders. It does not prove production latency, hosted API performance, customer workflow overhead, reviewer burden, throughput, SLA, or enforcement-path performance.

## Workloads

| Workload | Runs | p50 ms | p95 ms | Max ms | Result facts |
| --- | ---: | ---: | ---: | ---: | --- |
| `customer_evaluation_general` | 5 | 2.586 | 3.978 | 3.996 | actions=5, valid_ledgers=5, postures={'ALLOW': 1, 'DENY': 3, 'THROTTLE': 1} |
| `cloud_metadata_connector` | 5 | 3.532 | 3.996 | 4.073 | actions=6, valid_ledgers=6, postures={'DENY': 3, 'THROTTLE': 3} |
| `public_benchmark_ingestion` | 5 | 5.568 | 8.584 | 9.156 | actions=10, valid_ledgers=10, postures={'ALLOW': 2, 'DENY': 6, 'THROTTLE': 2} |
| `postcondition_evidence` | 5 | 3.02 | 4.87 | 5.263 | actions=10, observed=5, statuses={'gap': 1, 'pass': 4, 'unobserved': 5} |

## Reviewer Question

Which proof path should be timed inside a customer workflow, and what p95 overhead would make the integration unacceptable?
