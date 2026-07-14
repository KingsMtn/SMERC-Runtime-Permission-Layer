# Pilot DLL API

The Pilot DLL API exposes the Decision Lifecycle Ledger pilot loop over authenticated HTTP.

It is intentionally stateless in this version: callers submit the source ledger or benchmark DLL bundle with the request, and the API returns the appended ledger, metrics report, or Decision Certificate. Durable hosted ledger storage is a later deployment concern.

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

### `POST /v1/pilot/dll/certificate`

Required scope: `metrics.read`

Issues a digest-bound pilot Decision Certificate from a supplied verified DLL or pilot intake result.

Request shape:

```json
{
  "ledger": {},
  "decision_id": "dll:proxy-deploy-001::baseline",
  "issuer": "smerc-api:pilot-reviewer",
  "route_report": {}
}
```

The `ledger` field may be:

- a `smerc.pilot-ledger-intake-result.v1` object
- a `smerc.decision-lifecycle-ledger.v1` object
- a `smerc.benchmark-ledger-bundle.v1` object plus `decision_id`

The `route_report` field is optional. When supplied, it must be a `smerc.sparta-route.v1` report and the returned certificate binds to the route-report digest.

The response is an envelope containing:

- `certificate`: a `smerc.decision-certificate.v1` object
- `authenticated_principal`: the API principal that requested certificate issuance

The API does not accept a signing key in the JSON body. Hosted certificate signing should be configured as server-side key management in a later production deployment.

## Boundary

These endpoints make pilot evidence easier to submit, summarize, and package for review. They do not provide durable storage, legal recordkeeping, immutable infrastructure, managed certificate signing, SIEM integration, or compliance certification.
