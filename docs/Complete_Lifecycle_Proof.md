# Complete Lifecycle Proof

## Purpose

This proof shows SMERC operating as one connected system instead of separate parts.

It runs one synthetic production deployment request through runtime admission, recoverability scoring, SPARTa routing, Recovery Authority Gate, action-bound permit issuance, synthetic execution, and Decision Lifecycle Ledger evidence.

## Run It

```bash
python -m reference_engine.complete_lifecycle_proof
```

Outputs:

- `reports/complete_lifecycle/complete_lifecycle_proof.json`
- `reports/complete_lifecycle/Complete_Lifecycle_Proof_Report.md`

## Lifecycle

1. Runtime admission checks whether the request is shaped well enough to score.
2. SMERC scores the proposed wide production deployment.
3. SPARTa converts the initial posture into a tool route.
4. Recovery Authority Gate checks whether a paused action can be reopened.
5. SMERC scores the narrowed continuation action.
6. SPARTa creates a constrained execution route.
7. A short-lived action-bound permit is issued and verified.
8. The synthetic executor records a result.
9. Decision Lifecycle Ledger records request, evidence, evaluation, human interaction, execution, outcome, and learning recommendation events.

## Work / Result / Impact

Work: execute a complete metadata-only decision lifecycle from proposed action through review, continuation, permit, execution result, and ledger.

Result: the reference case returns `COMPLETE`: `ADMIT -> FREEZE -> PAUSE -> UNLOCK -> THROTTLE -> CONSTRAINED_EXECUTE -> permit verified -> execution succeeded -> ledger valid`.

Impact: reviewers can see SMERC as a full governance loop. The proof demonstrates that a risky automated action can pause before execution, cannot unlock itself, and can continue only after separate authority, fresh recovery evidence, a bounded route, a short-lived permit, and replayable ledger evidence.

## What This Proves

- The main reference components can operate together.
- The initial risky action pauses before execution.
- Unlock is separate from the proposing actor.
- Continuation uses a safer, narrowed action request.
- Permit verification checks that required controls were enforced.
- The Decision Lifecycle Ledger preserves the full decision history.

## Boundary

This is a deterministic, metadata-only proof. It does not execute production commands, prove production safety, certify compliance, validate customer demand, prove incident reduction, or replace a customer pilot.

The correct customer next step is still bounded shadow-mode evaluation with customer-owned metadata and reviewer judgment.
