# SMERC Decision Lifecycle Ledger

## Purpose

The SMERC Decision Lifecycle Ledger, or DLL, records the full life of a governed decision. It is designed to answer:

> What was requested, what evidence existed, what did SMERC decide, who changed the decision, what executed, what happened later, and what should governance learn?

DLL is not a replacement for SIEM, GRC, data retention systems, legal hold, or regulatory recordkeeping. It is a pilot-grade lifecycle evidence contract.

## Lifecycle Events

DLL records append-only events for one governed decision:

1. `REQUEST`: who or what initiated the action, when, where, and under what risk profile.
2. `EVIDENCE`: evidence available at decision time, confidence, missing evidence, dependencies, model version, and policy version.
3. `EVALUATION`: SMERC posture, recoverability score, structural state, entropy indicators, reason codes, and safeguards.
4. `HUMAN_INTERACTION`: reviewer acceptance, modification, override, or ignored recommendation with rationale.
5. `EXECUTION`: what actually executed, success or failure, duration, rollback activity, and rollback result.
6. `OUTCOME`: later judgment of correctness, consequences, control sufficiency, cost, recovery time, and impact.
7. `LEARNING_RECOMMENDATION`: proposed policy or calibration changes that require review before activation.

## Learning Boundary

SMERC DLL does not silently retrain a model or silently activate new policy. Learning records are recommendations only. Every learning recommendation must include:

- expected outcome
- actual outcome
- prediction error
- override effectiveness
- recommended policy updates
- confidence calibration changes
- suggested rule modifications
- activation status of `requires_review`

## Integrity Model

Each DLL record includes:

- sequence number
- event type
- actor
- timestamp
- previous record hash
- payload
- record hash

The hash chain detects accidental or deliberate modification of prior records. It does not by itself provide non-repudiation, managed key custody, immutable storage, legal retention, or regulatory compliance.

## Run The Example

```bash
python -m reference_engine.decision_lifecycle_ledger \
  --example \
  --json-output reports/decision_lifecycle_ledger_example.json \
  --markdown-output reports/Decision_Lifecycle_Ledger_Example.md \
  --pretty
```

Verify or render an existing ledger:

```bash
python -m reference_engine.decision_lifecycle_ledger \
  --input reports/decision_lifecycle_ledger_example.json \
  --markdown-output reports/Decision_Lifecycle_Ledger_Example.md
```

## Product Role

DLL turns SMERC from a single decision point into runtime governance infrastructure:

```text
SMERC decides posture
SPARTa routes posture into enforceable controls
DLL records request, evidence, decision, route, execution, outcome, and learning
DLL Intelligence summarizes near misses, overrides, rollback performance, drift, and review-gated policy recommendations
```

The first DLL implementation is deliberately local and deterministic. Production deployment would require durable storage, retention policy, access controls, privacy review, key management, export controls, and customer-specific compliance review.

See also `docs/DLL_Intelligence.md` for the multi-ledger analysis layer.
