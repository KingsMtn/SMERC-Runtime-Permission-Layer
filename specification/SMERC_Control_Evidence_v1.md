# SMERC Control Evidence v1

## Purpose

`smerc.control-evidence.v1` replaces an untrusted list of claimed controls with a short-lived receipt signed by the execution adapter assigned to one tenant and executor audience.

The receipt answers a narrow question: did the configured adapter attest that the required controls were applied to the exact action and permit immediately before consumption?

It does not prove the adapter implementation is correct, the referenced native record exists, or the signing key is uncompromised. Those claims require platform-native verification, managed keys, monitoring, and independent audit.

## Trust Boundary

Each verifier is configured for exactly one `(tenant_id, audience)` pair. The shared pilot key must be limited to the adapter that observes native enforcement results and the SMERC verifier service, not the proposing agent, permit issuer, or general API client.

The reference implementation uses HMAC-SHA256 for controlled pilots. Production implementations should use workload identity and HSM/KMS-backed asymmetric signatures or platform-native attestations.

## Compact Token

```text
base64url(header).base64url(payload).base64url(HMAC-SHA256(header.payload))
```

The header is fixed to:

```json
{
  "alg": "HS256",
  "kid": "alpha-control-evidence-2026-01",
  "typ": "SMERC-CONTROL-EVIDENCE"
}
```

The payload binds:

- receipt version and evidence ID
- tenant and executor audience
- adapter identity
- exact permit ID and action hash
- unique applied control results
- native mechanism and evidence reference for each result
- observation, issuance, and expiry times

## Control Result

Each result contains exactly:

| Field | Meaning |
| --- | --- |
| `control_id` | Required SMERC control identifier |
| `outcome` | Must be `applied`; failed or unknown controls cannot authorize consumption |
| `mechanism` | Native enforcement mechanism used by the adapter |
| `evidence_ref` | Bounded reference to the native execution record |
| `observed_at` | Unix time when the adapter observed the control result |

Receipts contain at most 64 unique controls. An observation cannot be later than receipt issuance or more than 120 seconds old. Receipt lifetime is 1 through 120 seconds and expiry is exclusive.

## Verification

When a verifier exists for the authenticated tenant and requested audience, permit consumption must:

1. Reject the legacy `enforced_controls` field.
2. Verify the receipt structure, key ID, signature, freshness, tenant, audience, and action hash.
3. Extract only controls with the `applied` outcome.
4. Verify the permit signature and required controls using that extracted set.
5. Require the receipt permit ID to equal the verified permit ID.
6. Recheck the stored decision, active policy, registered issuance digest, and prior consumption state.
7. Atomically consume the permit once.
8. Record the adapter, evidence ID, key ID, controls, expiry, and receipt digest without storing the token.

## Compatibility

If no control-evidence verifier is configured for a tenant and audience, the API accepts the existing `enforced_controls` list and labels the result `legacy_caller_assertion`. This path supports migration only and is not equivalent to signed adapter evidence.

## Versioning

The contract version is `smerc.control-evidence.v1`. Changes to canonical fields, signature rules, binding, freshness, or result semantics require a new version.
