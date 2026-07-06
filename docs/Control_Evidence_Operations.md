# Control Evidence Operations

## Configuration

Configure one adapter key for each tenant and executor audience:

```powershell
$env:SMERC_CONTROL_EVIDENCE_KEYS="alpha:github-actions-deployer=github-actions-adapter:alpha-control-evidence-2026-01:alpha-local-control-evidence-secret-0123456789"
```

The format is:

```text
tenant:audience=adapter-id:key-id:secret
```

Secrets require at least 32 characters. Every binding, key ID, and secret must be unique. The same tenant must also have an API credential and permit-signing key.

These are development-only values. Real keys belong in an approved secret manager and must never enter source control, logs, action artifacts, or decision reports.

## Adapter Sequence

1. Receive the action-bound permit and exact action envelope over a protected channel.
2. Apply each required control using the execution platform's native mechanism.
3. Read the native result rather than trusting caller-supplied text.
4. Create one result with mechanism, evidence reference, and observation time for every applied control.
5. Sign a receipt with the adapter key assigned to the permit tenant and audience.
6. Reserve the authenticated permit through `POST /v1/permits/prepare` before any native control runs.
7. Send the returned preparation ID and receipt token with the action and permit to `POST /v1/permits/consume`.
8. Execute the side effect only after SMERC returns `valid: true`.

Configured adapters send exactly:

```json
{
  "permit_token": "compact-permit-token",
  "action": {},
  "audience": "github-actions-deployer",
  "control_evidence_token": "compact-control-evidence-token"
}
```

The reference payload shape is in `examples/control_evidence/github_actions_canary_receipt.json`. The signer implementation is `reference_engine/control_evidence.py`.

## Native Evidence References

An evidence reference should identify a record the pilot team can independently retrieve, such as a GitHub run and job, cloud deployment operation, transaction approval record, or policy-enforcement event. Do not place credentials, raw customer data, or permit tokens in the reference.

## Failure Codes

| Code | Meaning |
| --- | --- |
| `control_evidence_required` | A configured adapter attempted legacy caller assertion. |
| `invalid_control_evidence_signature` | Receipt authenticity failed. |
| `control_evidence_binding_mismatch` | Tenant or audience does not match the configured adapter. |
| `control_evidence_action_mismatch` | Receipt is bound to another action. |
| `control_evidence_permit_mismatch` | Receipt is bound to another permit. |
| `required_control_evidence_missing` | Adapter did not provide every permit control. |
| `control_not_applied` | A result did not report successful application. |
| `stale_control_evidence` | Observation is outside the freshness window. |
| `control_evidence_expired` | Receipt expired before consumption. |

## Pilot Boundary

HMAC authenticates the configured adapter key; it does not prove the mechanism or evidence reference is truthful. A compromised adapter can sign false results. Production use requires managed workload identity, protected signing, native evidence retrieval, revocation, clock monitoring, and independent audit export.
