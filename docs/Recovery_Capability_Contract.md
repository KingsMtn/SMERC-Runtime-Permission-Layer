# Recovery Capability Contract

`smerc.recovery-capability.v1` is the machine-readable boundary between a tool's claim that an action can be recovered and Runtime Assurance's decision about whether that claim is usable.

## Why It Exists

`reversible: true` is too vague for consequential automation. The runtime needs to know the recovery mechanism, isolation boundary, trigger authority, tested rollback latency, evidence status, verified scope, mutation ceiling, and validity window.

The contract supports transaction rollback, snapshot restore, compensating action, version restore, and recreation from declaration. `NONE` is explicit so absence of recovery cannot be mistaken for missing metadata.

## Runtime Semantics

| Capability state | Runtime Assurance result |
| --- | --- |
| Verified, fresh, in scope, and within latency and mutation limits | Accept as evidence; add no permission or posture |
| Stale or unverified | `FREEZE` until verified |
| Scope, mutation, or rollback-latency limit exceeded | `FREEZE` for reduced scope or review |
| Failed test, absent mechanism, irreversible side effect, malformed content, tampering, expiry, or context mismatch | `DENY` |

## Authority Boundary

Every capability must declare `authority_effect: NONE` and `advisory_only: true`. Recovery evidence may constrain Runtime Assurance, but it cannot authorize an action, unlock a paused action, issue a permit, or weaken any stricter decision.

The capability is distinct from the Recovery Authority Gate. This contract answers, "what recovery can this integration demonstrably perform?" The gate answers, "who may reopen this paused action, using fresh evidence and a bounded route?"

## Integrity and Scope

The capability digest binds all content except its derived identifier and digest fields. Runtime evaluation also requires exact tool-family, operation, and environment matching. Resource patterns are descriptive evidence for downstream binding; adapters must still bind the actual resource at enforcement time.

## Claim Boundary

This is a pilot contract. A signed or digest-bound adapter statement does not independently prove that a cloud provider, database, workflow, or recovery mechanism will behave as claimed. Production use requires trustworthy adapter identity, external evidence, resource binding, replay protection, and observed recovery outcomes.
