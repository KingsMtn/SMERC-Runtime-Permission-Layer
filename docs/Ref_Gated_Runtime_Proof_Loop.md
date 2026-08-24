# Ref-Gated Runtime Proof Loop

## Purpose

This proof loop shows the intended SMERC runtime order:

```text
hard mechanical Ref gate -> SMERC recoverability scoring -> SPARTa route -> autonomy budget -> DLL evidence
```

The point is explicit: recoverability scoring must not replace hard pre-execution controls. If the typed contract, attestation, least-privilege check, or expected object shape fails, the action should be capped or held before scoring can justify normal execution.

## Why This Matters

External feedback on OpenSSF issue #50 correctly challenged the idea that recoverability alone is enough. If a bad action already left the system, the organization may have already lost the cleanest control point.

SMERC therefore treats the Ref pattern as a hard gate before recoverability scoring is allowed to matter.

## Run

From the repository root:

```bash
python -m reference_engine.ref_gated_runtime_proof --pretty
```

Generated files:

```text
reports/ref_gated_runtime_proof.json
reports/Ref_Gated_Runtime_Proof.md
```

## What The Proof Demonstrates

- Safe read-style tool calls with typed contract, attestation, least privilege, and expected object shape can proceed with lower friction.
- Destructive or financial tool calls can still be constrained, frozen, denied, or escalated even when the Ref gate passes.
- Ref-gate failures force high-risk hold behavior before recoverability can soften the decision.
- SPARTa converts posture into execution behavior.
- Autonomy budgeting summarizes whether the actor still has freedom to continue.
- Decision Lifecycle Ledger evidence records request, evidence, evaluation, execution, and outcome records.

## Reviewer Prompts

Use this proof loop to test:

1. Invalid object shape.
2. Weak authority but high reversibility.
3. Strong authority but low reversibility.
4. Safe read action with complete Ref evidence.
5. Repeated high-risk calls that reduce right to continue.

## Boundary

This is a deterministic local proof loop. It does not implement complete endpoint type safety, production MCP transport, prompt-injection defense, customer validation, compliance attestation, or production safety certification.
