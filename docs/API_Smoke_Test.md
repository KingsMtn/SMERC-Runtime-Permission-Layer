# API Smoke Test

## Purpose

The SMERC API smoke test gives a pilot operator a one-command way to verify that a local or hosted Runtime API can answer the basic review path:

- liveness
- persistence readiness
- schema discovery
- one recoverability evaluation
- runtime health metrics
- operator status

This is a pilot-readiness check. It is not a production certification, security audit, uptime guarantee, or proof of incident reduction.

## Command

Start the API in another terminal, then run:

```bash
python -m reference_engine.api_smoke_test \
  --base-url http://127.0.0.1:8000 \
  --token "$SMERC_API_KEY" \
  --pretty
```

Optional inputs:

```bash
python -m reference_engine.api_smoke_test \
  --base-url https://your-smerc-api.example \
  --token "$SMERC_API_KEY" \
  --action examples/recoverability_single_action.json \
  --latency-slo-ms 500 \
  --json-output reports/api_smoke_test.json \
  --markdown-output reports/API_Smoke_Test_Report.md \
  --pretty
```

## What Passing Means

A passing report means:

- the API responded to health and readiness checks
- schema discovery includes `/v1/operator/status`
- an action evaluation returned a replay ID
- the decision included a runtime observation
- runtime health reported latency after the live evaluation
- operator status included runtime health and was not blocked

## What Passing Does Not Mean

A passing report does not prove:

- production availability
- security certification
- customer-specific calibration
- enforcement safety
- incident reduction
- compliance readiness

## Outputs

Default outputs:

```text
reports/api_smoke_test.json
reports/API_Smoke_Test_Report.md
```

The report includes explicit failed checks and an evidence boundary suitable for external technical review.
