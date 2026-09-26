# Continuing Authority Contract

## The Future Failure Mode

Interoperable agents can delegate opaque, asynchronous work across runtimes and organizations. A task can therefore begin with valid authority and finish after the user, policy, credential, model, tool, budget, or accountable organization has changed.

SMERC calls this **authorization afterlife**.

Identity and admission checks establish whether work may begin. Continuing Authority asks a later question at every consequential checkpoint:

> Is the authority that allowed this work to begin still valid, accountable, continuous, and sufficient for the consequence about to occur?

## Runtime Assurance And Action Assurance

Runtime Assurance owns the execution boundary. It reconciles the current authority epoch before an individual action continues or settles.

Action Assurance can observe a collective delegation graph, collect descendant acknowledgements, and identify incomplete invalidation propagation. Its evidence cannot grant authority or relax an RA decision.

## Reference Proof

`reference_engine/continuing_authority.py` and `tests/test_continuing_authority.py` demonstrate:

1. continuation under an unchanged authority epoch
2. quarantine after epoch change, revocation, or expiry
3. compensation when stale authority already produced partial effects
4. orphan detection when no accountable principal remains active
5. revalidation after policy triggers or checkpoint discontinuity
6. settlement only with current authority and complete evidence
7. visible failure when descendant invalidation is unconfirmed

## Non-Claim

This is a deterministic reference proof. It is not production validation, regulatory approval, distributed consensus, or evidence that revocation can always cross a partition before a downstream effect. Those are explicit pilot and adversarial-test obligations.
