# Delegated Continuance Contract

## Purpose

The Delegated Continuance Contract controls whether an autonomous workflow still has authority to continue after work is delegated, delayed, resumed, or expanded.

Authentication and IAM answer who may request an operation. The contract answers a different runtime question:

> Does this agent still have sufficient inherited authority, intent alignment, budget, time, and recovery evidence for this next action?

## Contract

Each signed contract binds:

- originating user and current agent
- original intent digest
- parent contract digest and delegation depth
- permitted capabilities and resources
- cumulative action, scope, and cost budgets
- expiry
- checkpoint frequency
- cleanup obligations

A child contract must attenuate its parent. It cannot add capabilities or resources, increase a budget, extend expiry, weaken checkpoint frequency, remove cleanup obligations, or exceed maximum delegation depth.

## Runtime Decisions

- `CONTINUE`: the next action remains inside the delegated envelope.
- `BLOCK`: intent, capability, resource, or cumulative budget is outside the envelope.
- `EXPIRED`: delayed work must be reauthorized before resuming.
- `CHECKPOINT_REQUIRED`: the workflow must preserve reviewable state before continuing.
- `CLEANUP_REQUIRED`: a side-effecting action lacks the cleanup plan required by the contract.

Every evaluation records hashes for the signed contract and proposed action, the reevaluation time, and remaining authority.

## Intended Proof

The reference tests model a coordinator delegating a bounded ephemeral-branch update to a worker. They demonstrate:

1. allowed continuation under attenuated authority
2. rejection of delegated capability expansion
3. blocking cumulative scope expansion
4. denial of an expired task on resumption
5. checkpoint and cleanup requirements before side effects
6. rejection of contract tampering

## Boundary

This is a deterministic reference contract, not an identity provider, IAM replacement, production key-management system, or claim of production validation. Production deployment requires customer-owned identity binding, durable consumption storage, replay protection, key rotation, clock controls, and independently reviewed policy thresholds.
