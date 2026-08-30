# Serious Report Performance

SMERC serious reports should include performance evidence where it matters.

This harness measures local p50, p95, and maximum latency for the report builders a reviewer is most likely to run during technical diligence:

- general customer evaluation
- cloud metadata connector
- public benchmark ingestion
- postcondition evidence

Run:

```bash
python -m reference_engine.serious_report_performance --iterations 5 --pretty
```

Outputs:

- `reports/Serious_Report_Performance.md`
- `reports/serious_report_performance.json`

## Work / Result / Impact

Work: run serious SMERC proof paths repeatedly and summarize local execution latency.

Result: reviewers receive local p50, p95, and maximum timing for the general customer evaluation, cloud metadata connector, public benchmark ingestion, and postcondition evidence paths.

Impact: technical reviewers can see whether proof generation is lightweight enough for local evaluation, while customer pilots still measure production p50, p95, workflow overhead, and reviewer impact in their own environment.

## Evidence Boundary

This is local reference performance evidence for report builders.

It does not prove production latency, hosted API performance, customer workflow overhead, reviewer burden, throughput, SLA, or enforcement-path performance.

## Reviewer Question

Which proof path should be timed inside a customer workflow, and what p95 overhead would make the integration unacceptable?
