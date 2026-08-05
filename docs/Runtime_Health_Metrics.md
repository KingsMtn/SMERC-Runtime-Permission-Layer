# Runtime Health Metrics

SMERC needs an operator-visible health surface before it can be credible in a customer pilot.

This module reports:

- decision volume
- posture distribution
- observed evaluation latency
- p50, p95, and p99 latency
- unavailable evaluation rate
- fail-closed count and rate
- operational checks for latency, observations, evidence labeling, and unavailable behavior

## Command

```bash
python -m reference_engine.runtime_health_metrics --pretty
```

Outputs:

```text
reports/runtime_health_metrics.json
reports/Runtime_Health_Metrics.md
```

## API

```bash
curl -H "Authorization: Bearer $SMERC_API_KEY" \
  "http://127.0.0.1:8000/v1/runtime/health-metrics?limit=50&latency_slo_ms=250"
```

The API endpoint is tenant-scoped and requires `metrics.read`. Runtime API evaluations now persist a compact `runtime_observation` on each stored decision, including integration status and measured evaluation latency. The health endpoint derives its latency samples from those stored decision records when available.

If a report is generated from imported historical decisions or benchmark artifacts that do not contain runtime observations, latency remains unknown instead of being estimated.

## Why This Matters

CISOs and platform teams will not only ask whether SMERC makes useful decisions. They will ask whether it can be observed while running:

- Is it adding unacceptable latency?
- How often is the integration unavailable?
- Does it fail closed when enforcement depends on it?
- Are health metrics based on customer telemetry or sample/reference observations?

The reference report is intentionally bounded. It shows the reporting shape and local/API-observed prototype latency, not a production SLA.

## Evidence Boundary

The checked-in sample observations and API-observed local timings are reference evidence for demonstration. They must be replaced or supplemented with customer telemetry before making claims about production latency, availability, incident reduction, or SLA compliance.
