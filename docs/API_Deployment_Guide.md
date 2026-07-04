# SMERC Pilot API Deployment Guide

## Deployment Boundary

The API is a controlled pilot vehicle for recoverability-aware action scoring. It separates the deterministic engine from authentication, transport, idempotency, and audit persistence.

It is appropriate for shadow-mode evaluation with action metadata. It is not represented as a production-certified enforcement service.

## Local Development

Unauthenticated mode must be explicit:

```bash
python api_server.py \
  --host 127.0.0.1 \
  --port 8788 \
  --audit-db :memory: \
  --allow-unauthenticated
```

```bash
curl http://127.0.0.1:8788/health
curl http://127.0.0.1:8788/ready
curl -X POST http://127.0.0.1:8788/v1/evaluate \
  -H "Content-Type: application/json" \
  --data @examples/recoverability_single_action.json
```

## Authenticated Pilot Mode

Use `SMERC_API_PRINCIPALS` for scoped tenant credentials. Entries use `tenant:principal:scope+scope=secret` and are separated by commas. `SMERC_API_KEYS=tenant=secret` remains as an all-scope compatibility mode.

```bash
export SMERC_API_PRINCIPALS="platform-team:github-proposer:actions.evaluate=platform-proposer-local-secret-012345,platform-team:pilot-reader:decisions.read=platform-reader-local-secret-01234567"
export SMERC_AUDIT_DB="./smerc_audit.sqlite3"
export SMERC_POLICY_DIR="./examples/policies"
python api_server.py --host 127.0.0.1 --port 8788
```

Evaluate and persist one action:

```bash
curl -X POST http://127.0.0.1:8788/v1/evaluate \
  -H "Authorization: Bearer platform-proposer-local-secret-012345" \
  -H "Idempotency-Key: github-run-1001" \
  -H "Content-Type: application/json" \
  --data @examples/recoverability_single_action.json
```

Listing decisions requires a separate `decisions.read` principal:

```bash
curl "http://127.0.0.1:8788/v1/decisions?limit=25&posture=THROTTLE" \
  -H "Authorization: Bearer platform-reader-local-secret-01234567"
```

Retrieve a decision:

```bash
curl http://127.0.0.1:8788/v1/decisions/REPLAY_ID \
  -H "Authorization: Bearer platform-reader-local-secret-01234567"
```

## Endpoint Contract

| Endpoint | Authentication | Purpose |
| --- | --- | --- |
| `GET /health` | No | Process liveness |
| `GET /ready` | No | Audit-store readiness |
| `GET /schema` | No | Input and endpoint contract |
| `POST /v1/evaluate` | Bearer | Evaluate and store one action |
| `POST /v1/language/evaluate` | Bearer | Validate, compile, evaluate, and store one `smerc.action.v1` envelope |
| `POST /v1/permits/issue` | Bearer | Issue one short-lived action-bound permit for an eligible enforcement decision |
| `POST /v1/permits/consume` | Bearer | Verify, register controls, and atomically consume a permit |
| `POST /v1/batch` | Bearer | Evaluate and store a bounded batch |
| `GET /v1/decisions` | Bearer | List decision summaries for the authenticated tenant |
| `GET /v1/decisions/{replay_id}` | Bearer | Retrieve one decision for the authenticated tenant |
| `POST /v1/decisions/{replay_id}/reviews` | Bearer | Record one immutable pseudonymous review |
| `GET /v1/decisions/{replay_id}/reviews` | Bearer | List reviews for one tenant decision |
| `GET /v1/review-queue` | Bearer | List pending, reviewed, or all tenant decisions |
| `GET /v1/pilot/metrics` | Bearer | Retrieve denominator-aware pilot measurements |
| `GET /v1/security-events` | Bearer | Retrieve tenant-scoped attributed permit and review events |

Legacy `/evaluate` and `/batch` aliases remain available. New integrations should use `/v1`.

## Idempotency

Send `Idempotency-Key` on single evaluations. Repeating the same key and payload returns the original decision and sets `X-SMERC-Idempotent-Replay: true`. Reusing the key with a different payload returns HTTP `409`.

This prevents a workflow retry from producing multiple audit decisions for the same proposed action.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `SMERC_API_KEYS` | none | Legacy all-scope `tenant=secret` mappings |
| `SMERC_API_PRINCIPALS` | none | Recommended scoped `tenant:principal:scope+scope=secret` credentials |
| `SMERC_AUDIT_DB` | `smerc_audit.sqlite3` | SQLite audit path |
| `SMERC_MAX_BODY_BYTES` | `262144` | Maximum JSON request body |
| `SMERC_MAX_BATCH_SIZE` | `100` | Maximum actions per batch |
| `SMERC_CORS_ORIGINS` | none | Comma-separated trusted browser origins |
| `SMERC_POLICY_DIR` | none | Directory of tenant-scoped `smerc.policy.v1` revisions |
| `SMERC_PERMIT_KEYS` | none | Optional `tenant=key-id:secret` permit-signing mappings; secrets require at least 32 bytes |
| `PORT` | `8788` | Listening port |

At least one legacy key or scoped principal is required. Do not commit credentials or put them in URLs. Rotate pilot credentials when personnel or integration scope changes. Legacy keys receive all tenant scopes; scoped principals are recommended for new pilots. See `Scoped_Workload_Identity.md`.

Permit signing is disabled when `SMERC_PERMIT_KEYS` is empty. Signing tenants must also have a legacy or scoped API credential. Permit tokens are bearer capabilities and must not enter logs or report artifacts. Full issuance and consumption procedures are in `Action_Bound_Permit_Operations.md`.

The authenticated tenant selects the policy; clients cannot name a policy in an action request. The server chooses the latest effective revision for that tenant and refuses startup when a configured tenant has no effective revision. Tenants without configured policy files use the identified reference policy in `OBSERVE` mode.

## Pilot Review Console

The dependency-free console in `pilot_console/` requires its exact browser origin in `SMERC_CORS_ORIGINS`. For local use:

```bash
export SMERC_CORS_ORIGINS="http://127.0.0.1:8790"
python -m http.server 8790 --bind 127.0.0.1 --directory pilot_console
```

Remote console deployments must use HTTPS. The bearer key is held only in tab memory. The console intentionally does not use local storage, session storage, cookies, analytics, or third-party runtime assets.

## Docker

```bash
export SMERC_API_PRINCIPALS="platform-team:pilot-console:actions.evaluate+decisions.read+reviews.read+reviews.write+metrics.read=development-console-secret-2026-rotate"
docker compose up --build
```

The Compose profile mounts `smerc-audit-data` at `/data` and stores the audit database there.

## Render

The included `render.yaml` describes a paid starter service with a persistent disk mounted at `/var/data`. Render's free filesystem is ephemeral and should not be used when pilot audit records must survive restarts or deploys.

During initial Blueprint creation, Render prompts for credential values. Set `SMERC_API_PRINCIPALS` for new pilots. `SMERC_API_KEYS` is required only when an existing all-scope integration still needs compatibility access. For an existing Blueprint, set or rotate secrets in the Render dashboard because `sync: false` values are not updated automatically.

Expected controls:

- start command: `python api_server.py --host 0.0.0.0 --port $PORT`
- health check: `/health`
- audit database: `/var/data/smerc_audit.sqlite3`
- persistent disk: `/var/data`
- scoped-principal secrets: dashboard-managed `SMERC_API_PRINCIPALS`
- optional legacy all-scope secret: dashboard-managed `SMERC_API_KEYS`
- optional permit-signing secret: dashboard-managed `SMERC_PERMIT_KEYS`

## Pilot Limitations

- SQLite is suitable for one pilot-service instance, not horizontal scaling.
- API keys are a pilot credential model, not enterprise IAM federation.
- Scoped principals provide endpoint separation but remain static bearer credentials without managed expiry or revocation.
- The service does not yet provide managed key rotation, SSO, RBAC, retention automation, SIEM export, or customer-managed encryption keys.
- Permit replay prevention is single-instance SQLite state, not a distributed capability service.
- Thresholds require customer-specific calibration before enforcement.
- Security, privacy, legal, and architecture owners must approve production use.
