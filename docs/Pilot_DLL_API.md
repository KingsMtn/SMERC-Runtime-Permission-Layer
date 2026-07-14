# Pilot DLL API

The Pilot DLL API exposes the Decision Lifecycle Ledger pilot loop over authenticated HTTP.

It is intentionally stateless in this version: callers submit the source ledger or benchmark DLL bundle with the request, and the API returns the appended ledger or metrics report. Durable hosted ledger storage is a later deployment concern.

## Endpoints

### `POST /v1/pilot/dll/intake`

Required scope: `reviews.write`

Appends pilot evidence to a supplied DLL or benchmark DLL bundle.

Request shape:

```json
{
  "ledger": {},
  "decision_id": "dll:proxy-deploy-001::baseline",
  "intake": {}
}
```

The `ledger` field may be:

- a `smerc.decision-lifecycle-ledger.v1` object
- a `smerc.benchmark-ledger-bundle.v1` object plus `decision_id`

The `intake` field must be a `smerc.pilot-ledger-intake.v1` object.

The authenticated tenant must match the source ledger and the intake record.

### `POST /v1/pilot/dll/metrics`

Required scope: `metrics.read`

Summarizes supplied completed DLL evidence.

Request shape:

```json
{
  "ledgers": []
}
```

Each item may be:

- a `smerc.pilot-ledger-intake-result.v1` object
- a `smerc.decision-lifecycle-ledger.v1` object

All ledgers must match the authenticated tenant.

## Boundary

These endpoints make pilot evidence easier to submit and summarize. They do not provide durable storage, legal recordkeeping, immutable infrastructure, SIEM integration, or compliance certification.
