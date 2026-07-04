# SMERC Action-Bound Permit v1

## Purpose

The Action-Bound Permit converts an eligible SMERC decision into a short-lived capability that an execution adapter can verify immediately before a side effect. It closes part of the gap between deciding that an action may proceed and proving which exact action was authorized.

The permit does not make an unsafe action safe. It does not replace workload identity, IAM, transaction authorization, code review, or the executor's native controls.

## Issuance Preconditions

A permit may be issued only when all conditions hold:

1. The request is a valid `smerc.action.v1` envelope.
2. Its canonical SHA-256 action hash equals the stored decision action hash.
3. The decision belongs to the authenticated tenant.
4. The decision policy is still the active tenant policy.
5. The policy mode is `ENFORCE`.
6. The evidence ceiling is `LIMITED_ENFORCE` or `CALIBRATED_ENFORCE`.
7. The posture is `ALLOW` or `THROTTLE`.
8. The posture agrees with the decision enforcement state.
9. No permit has already been issued for the same tenant, replay, and executor audience.

`FREEZE`, `DENY`, and `ESCALATE` never produce permits.

## Token Format

The compact token contains three base64url segments:

```text
base64url(header).base64url(payload).base64url(HMAC-SHA256(header.payload))
```

The header fixes `alg` to `HS256`, `typ` to `SMERC-PERMIT`, and identifies the tenant signing key with `kid`. The verifier rejects alternate algorithms or unknown header fields.

The payload is validated against `schemas/smerc-action-bound-permit-v1.schema.json` and binds:

- permit, tenant, and executor-audience identifiers
- canonical action hash
- decision replay ID
- `release` or `constrain` authorization
- required control codes
- policy ID, revision, hash, mode, and evidence ceiling
- issuance, activation, and expiry times
- a single-use limit

Maximum lifetime is 300 seconds. Expiry is exclusive.

## Constrained Authorization

An `ALLOW` permit authorizes `release`. A `THROTTLE` permit authorizes only `constrain` and carries every decision control except the bookkeeping controls `execute` and `record_replay`.

When a control-evidence verifier is configured, the consuming adapter must provide a signed `smerc.control-evidence.v1` receipt derived from native enforcement results. Consumption fails when the receipt is stale, incorrectly bound, invalidly signed, or missing any required control. Unconfigured audiences retain a migration-only caller-assertion path that is explicitly labeled as legacy.

## Verification And Consumption

Before execution, the consumer must verify:

- exact HMAC signature and supported key ID
- token structure and bounded lifetime
- authenticated tenant and expected audience
- canonical hash of the proposed action
- active policy hash and stored decision relationship
- required signed control evidence, when configured
- registered issuance digest
- absence of prior consumption

Successful consumption is recorded atomically in SQLite for the single-instance pilot. A second consumption returns `permit_already_consumed`.

## Security Boundaries

- HMAC provides shared-key authenticity, not public nonrepudiation.
- A compromised signing key can mint valid-looking tokens.
- A compromised API credential can request permits for eligible decisions.
- Scoped principals separate proposer, issuer, and executor API authority.
- The pilot has no permit revocation list; policy replacement invalidates outstanding permits.
- SQLite is not a distributed replay-prevention system.
- Signed adapter evidence improves authenticity and binding but does not prove the adapter or referenced native mechanism is truthful.
- The permit proves authorization binding, not successful execution or rollback.
- Production use requires managed HSM/KMS signing, workload identity, key rotation, distributed atomic consumption, clock monitoring, revocation, native evidence verification, and independent audit.

## Versioning

The initial contract is `smerc.permit.v1`. Any change to canonical claims, signature rules, lifetime semantics, or consumption behavior requires a new version.
