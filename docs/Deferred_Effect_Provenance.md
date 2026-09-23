# Deferred Effect Provenance

## Purpose

An agent can cause a privileged action without invoking the privileged tool itself. It can write code, infrastructure configuration, prompts, workflows, queue messages, or agent definitions that another identity executes later.

Deferred Effect Provenance prevents that handoff from laundering authority.

## Provenance Contract

Each signed artifact attestation binds:

- exact content digest and artifact type
- originating agent and delegated-contract digest
- originating intent
- maximum authority ceiling
- allowed and prohibited future effects
- unresolved obligations
- expiration and review requirement
- parent attestations for copies, transformations, and combined artifacts

Derived artifacts inherit the intersection of allowed effects, union of prohibitions and obligations, earliest expiry, and lowest authority ceiling. Copying, renaming, formatting, rebasing, or combining an artifact therefore cannot silently increase its future authority.

## Material Review

A signed review is bound to the exact attestation and content digest. It can approve only effects already inside the inherited authority and can satisfy named obligations. It cannot promote preview-only material into production authority.

## Proof Cases

The tests show that:

1. a production executor cannot deploy a preview-only artifact
2. copied and transformed artifacts retain restrictions
3. combined artifacts inherit the most restrictive parents
4. an exact-content material review can satisfy obligations
5. changed content and expired provenance are blocked
6. attestation tampering is rejected

## Boundary

This is a deterministic reference contract, not a software-composition-analysis product, code-signing infrastructure, production provenance store, or substitute for review. Production use requires repository and build-system integration, durable lineage storage, trusted reviewer identity, key rotation, revocation, merge semantics, artifact canonicalization, and enforcement at deployment and execution boundaries.
