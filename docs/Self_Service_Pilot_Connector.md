# Self-Service Pilot Connector

The Self-Service Pilot Connector gives a reviewer one simple way to test SMERC with sample events before a live integration.

It accepts a bundle of metadata-only events and returns a compact decision package.

Supported event types:

- `action_language`: SMERC Action Language requests for GitHub Actions, deployment, cloud, or workflow actions.
- `mcp_transport`: local JSON-RPC-style MCP `tools/call` envelopes.

## Why This Exists

SMERC already includes deeper components: recoverability scoring, SPARTa routing, Decision Lifecycle Ledger evidence, MCP tool governance, and MCP proxy samples.

This connector gives a prospect a lower-friction path:

1. paste or adapt a few non-secret action examples,
2. run one command,
3. inspect which actions SMERC would allow, throttle, freeze, deny, or escalate,
4. decide whether a real observe-mode pilot is worth discussing.

## Run

```bash
python -m reference_engine.self_service_pilot_connector \
  --bundle examples/self_service_pilot_bundle.json \
  --json-output reports/self_service_pilot_connector_report.json \
  --markdown-output reports/Self_Service_Pilot_Connector_Report.md \
  --pretty
```

## Output

The report includes:

- total events evaluated,
- source counts,
- posture counts,
- forwarded and blocked MCP calls,
- highest irreversible-exposure examples,
- pilot-fit classification,
- recommended next action,
- per-event scores, reason codes, controls, and replay IDs.

## Evidence Boundary

This is a self-service review tool, not proof of production readiness. It should use only non-secret metadata. A real pilot still requires customer-approved sample events, reviewer labels, latency measurement, stop conditions, and human owner accountability.
