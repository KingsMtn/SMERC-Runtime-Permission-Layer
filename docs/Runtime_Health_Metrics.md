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

The API endpoint is tenant-scoped and requires `metrics.read`. The first API version summarizes stored decisions and reports latency as unknown unless runtime observations are available through a supplied report or future telemetry store.

## Why This Matters

CISOs and platform teams will not only ask whether SMERC makes useful decisions. They will ask whether it can be observed while running:

- Is it adding unacceptable latency?
- How often is the integration unavailable?
- Does it fail closed when enforcement depends on it?
- Are health metrics based on customer telemetry or sample/reference observations?

The reference report is intentionally bounded. It shows the reporting shape, not a production SLA.

## Evidence Boundary

The checked-in sample observations are reference/local observations for demonstration. They must be replaced with customer telemetry before making claims about production latency, availability, incident reduction, or SLA compliance.
