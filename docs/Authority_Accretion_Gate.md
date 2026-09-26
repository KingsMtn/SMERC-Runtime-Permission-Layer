# Authority Accretion Gate

## The Gap

An agent can begin with valid authority and later acquire a credential, account, service, tool, compute resource, or another agent. Transaction, payment, OAuth, and fulfillment checks do not necessarily decide whether the acquired resource may become usable authority inside the running task.

SMERC calls this **authority accretion**: authority that enters after admission and may silently widen the original execution envelope.

## Contract

Every acquired resource starts quarantined. Runtime Assurance compares its resolved provider provenance and actual capabilities against the current authority epoch and original bounded envelope. The gate checks resource kind, provider, capabilities, effects, delegation depth, persistence, and spend.

- `ELIGIBLE_FOR_ACTIVATION` means the resource remains inside the envelope, but a separate executor must activate it.
- `QUARANTINE` means the resource is stale, unverified, improperly introduced, or would expand authority.

Every result sets `authority_effect: NONE` and `should_activate: false`. This component never activates a credential or resource.

## Public Work Considered

Authenticated-delegation research establishes the need for auditable authority chains. The AcquireBound paper identifies the post-fulfillment activation gap for resources obtained by agents. Microsoft's MIT-licensed Agent Governance Toolkit demonstrates platform demand for deterministic policy enforcement, lifecycle controls, and evidence.

SMERC's narrower contribution connects acquired authority to its recoverability, consequence, continuing-authority, and settlement contracts. This is original SMERC code informed by public concepts; no third-party implementation code was copied.

## Reference Proof

`reference_engine/authority_accretion.py` and `tests/test_authority_accretion.py` demonstrate quarantine before evaluation, current-epoch and provenance reconciliation, and non-expansion across capability, effect, delegation, persistence, and spend.

## Non-Claim

This is a deterministic reference proof, not a credential broker, cloud control plane, payment authorization service, formal provider verification, or production isolation boundary. Production use requires authenticated provider resolvers, atomic activation, durable single-use permits, customer policy, and adversarial testing.
