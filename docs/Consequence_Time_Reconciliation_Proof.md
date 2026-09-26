# Consequence-Time Reconciliation Proof

## Purpose

This proof connects three SMERC contracts at the moment an autonomous task attempts to commit or settle:

1. Delegated Continuance checks attenuated capability, resource, time, checkpoint, cleanup, and budget limits.
2. Authority Accretion checks whether power acquired after admission remains inside the original envelope.
3. Continuing Authority checks whether consent, authority epoch, accountable lineage, revocation, checkpoint continuity, and settlement evidence remain current.

No single passing checkpoint can override another failing checkpoint. A valid delegation cannot hide stale authority. Current authority cannot hide an exhausted delegated budget. Recoverable acquired power cannot activate outside its original envelope.

## Outcomes

- `SETTLE`: all three checkpoints pass at consequence time.
- `QUARANTINE`: at least one checkpoint fails before commitment and no partial effect requires compensation.
- `COMPENSATE`: continuing authority is stale or revoked after partial effects occurred.

The coordinator always emits `authority_effect: NONE`. Only `SETTLE` sets `should_commit: true`; the proof itself executes no external action.

## Scenarios

The focused test demonstrates:

- a fully current and bounded chain that may settle;
- authority-epoch change plus acquired capability expansion that quarantines before commit;
- revocation after partial effects that requires compensation;
- exhausted delegated action budget that cannot be hidden by otherwise-current authority.

## Non-Claim

This is deterministic reference orchestration, not a production transaction coordinator, identity provider, credential broker, distributed consensus protocol, or guarantee of revocation delivery across partitions. Production use requires customer-owned identity and policy sources, authenticated resource resolvers, durable atomic state, executor enforcement, and adversarial integration testing.
