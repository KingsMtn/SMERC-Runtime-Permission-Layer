# SMERC Continuing Authority Contract v1

## Purpose

`smerc.continuing-authority.v1` reconciles an earlier authority grant with current runtime facts before an autonomous task continues or settles a consequence.

It addresses authorization afterlife: work that began legitimately but remains active after its authority, accountable principal, policy epoch, tool version, or evidence state changes.

## Inputs

The grant identifies:

- authority epoch and accountable lineage
- issue and expiry times
- events that force revalidation
- last accepted checkpoint digest
- settlement requirements
- known descendant contracts that must receive invalidation

The runtime observation identifies:

- the current authority epoch and observation time
- explicit revocations and trigger events
- currently active accountable principals
- descendant invalidation acknowledgements
- current checkpoint and partial-effect state
- evidence available for settlement

## Decisions

- `CONTINUE`: the grant remains current and continuous.
- `REVALIDATE`: current authority exists, but a trigger, checkpoint discontinuity, or missing settlement requirement requires a fresh decision.
- `QUARANTINE`: authority is stale or revoked and no partial effect requires compensation.
- `COMPENSATE`: authority is stale or revoked after partial effects occurred.
- `SETTLE`: authority remains current and every required settlement fact is present.
- `ORPHANED`: no principal in the authority lineage remains active and accountable.

Every result has `authority_effect: NONE`. The contract reports reconciliation evidence; it cannot issue, extend, or restore authority.

## Relationship To Existing Contracts

The Delegated Continuance Contract constrains what a child may inherit and whether its next proposed action remains inside that envelope. Continuing Authority adds a temporal reconciliation step: it asks whether the authority behind the envelope is still current and whether invalidation reached all known descendants.

Consequence Settlement may consume a `SETTLE` result as evidence. It must not treat any other result as settlement authority.

Collective Action Assurance may aggregate descendant acknowledgements and authority-epoch observations. It remains advisory and cannot grant Runtime Assurance permission.

## Boundary

This reference contract does not provide an identity provider, revocation transport, trusted clock, distributed consensus, key management, compensation executor, or legal determination of accountability. Production use requires customer-owned bindings for those capabilities and independent review of failure behavior during partitions and delayed delivery.
