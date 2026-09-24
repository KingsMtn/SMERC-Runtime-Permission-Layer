# SMERC Adversarial Challenge Corpus

## Initial Challenges

The first corpus turns six high-value agentic failure modes into repeatable Contained Challenge Scenarios:

1. Authority laundering through a later privileged executor.
2. Delegated-agent drift beyond inherited intent or capability.
3. Concurrent exhaustion of shared consequence capacity.
4. Reuse of stale or context-mismatched credentials.
5. Rollback claims that leave residual consequences.
6. Delayed execution of expired or modified artifacts.

Each generated scenario is digest-bound and inherits SMERC Adversarial Assurance containment requirements. The corpus prohibits production, external, and third-party targets.

## Suite Semantics

- `PASS`: every configured challenge observed its expected control holding.
- `FAIL`: at least one control miss was observed.
- `INCOMPLETE`: no miss was observed, but at least one challenge did not run or stopped without a conclusion.

A missing executor is always `INCOMPLETE`, never a pass. The supplied simulation adapter is deterministic and performs no external action. It exists for contract and CI regression testing, not as production security evidence.

## Next Integration Boundary

Future adapters may connect these scenarios to customer-owned ephemeral AWS accounts or local emulators. Such adapters must preserve the same containment envelope, use scoped short-lived identity, reserve consequence capacity before execution, verify cleanup, and emit portable evidence. The corpus itself grants no authority to access or test a system.

