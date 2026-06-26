# SMERC Recoverability API Deployment Guide

## Local Run

```bash
python api_server.py --host 127.0.0.1 --port 8788
```

Health check:

```bash
curl http://127.0.0.1:8788/health
```

Evaluate one action:

```bash
curl -X POST http://127.0.0.1:8788/evaluate \
  -H "Content-Type: application/json" \
  --data @examples/recoverability_single_action.json
```

The `/evaluate` endpoint expects one JSON object. The `/batch` endpoint expects a list.

Batch example:

```bash
curl -X POST http://127.0.0.1:8788/batch \
  -H "Content-Type: application/json" \
  --data @examples/recoverability_action_requests.json
```

## Render Deployment

The repository includes `render.yaml`.

Expected Render settings:

- runtime: Python
- build command: `pip install -r requirements.txt`
- start command: `python api_server.py --host 0.0.0.0 --port $PORT`
- health check path: `/health`

## API Input Shape

Required fields:

- `action_id`
- `description`
- `actor`
- `tool`
- `action_type`
- `base_action_risk`
- `reversibility`
- `containment_strength`
- `rollback_latency`
- `evidence_validity`
- `anomaly_pressure`
- `impact_scope`
- `cancel_reliability`
- `authorization_confidence`
- `external_side_effect`
- `sensitive_data`

Numeric fields are `0.0` to `1.0`.

## API Output Shape

The API returns:

- `posture`
- `enforcement_state`
- `scores`
- `reason_codes`
- `controls`
- `plain_english_summary`
- `replay_id`
- `replay`

## Security Notes

This API is a reference implementation for pilot evaluation. A production service would still require:

- authentication
- authorization
- tenant isolation
- request signing or trusted ingress
- rate limiting
- persistent audit storage
- secret management
- production logging and monitoring
- legal/security review
