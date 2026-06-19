# Reversibility-Weighted Authorization v1

## Purpose

Reversibility-weighted authorization is a SMERC mechanism that determines whether an automated action should be released, constrained, blocked, or suspended based on the relationship between action risk and the system's ability to reverse, contain, or safely unwind the action.

The mechanism is intended to be narrower and more technical than a general governance or policy-engine claim.

## Input Signals

All numeric signals are normalized from `0.0` to `1.0`.

| Signal | Meaning |
| --- | --- |
| `base_action_risk` | Inherent risk of the proposed action before reversibility adjustment. |
| `reversibility` | Ability to undo, claw back, roll back, stop, or safely unwind the action. |
| `containment_strength` | Ability to limit downstream effects if the action misfires. |
| `rollback_latency` | Time and operational burden required to reverse the action. Higher is worse. |
| `evidence_validity` | Evidence quality supporting the action. |
| `anomaly_pressure` | Suspicious, unusual, or out-of-distribution pressure. |
| `impact_scope` | Blast radius across money, users, systems, safety, data, or operations. |

## Output

| Output | Meaning |
| --- | --- |
| `decision` | `RELEASE`, `CONSTRAIN`, `BLOCK`, or `SUSPEND`. |
| `irreversible_exposure_score` | Risk exposure created by weak reversibility, broad impact, anomaly, and rollback latency. |
| `reversible_capacity_score` | Ability to safely undo, contain, or recover from the action. |
| `risk_adjusted_authorization_score` | Release-support score after reversibility and exposure are considered. |
| `reason_codes` | Interpretable decision drivers. |
| `controls` | Concrete enforcement controls. |

## Mathematical Model

Let:

- `R` = reversibility
- `C` = containment strength
- `L` = rollback latency
- `E` = evidence validity
- `A` = anomaly pressure
- `B` = base action risk
- `I` = impact scope

### Reversible Capacity Score

```text
RCS = 0.46R + 0.30C + 0.14(1 - L) + 0.10E
```

`RCS` measures the system's ability to recover if the action is wrong.

### Irreversible Exposure Score

```text
IES = 0.34(1 - R) + 0.22B + 0.18I + 0.16A + 0.10L
```

`IES` measures how much unrecoverable exposure is created by the action.

### Risk-Adjusted Authorization Score

```text
RAAS = 0.55RCS + 0.25E + 0.20(1 - IES)
```

`RAAS` measures whether the action has enough recoverability and evidence support to proceed.

All scores are clipped to `[0.0, 1.0]`.

## Decision Rules

### SUSPEND

Select `SUSPEND` when:

```text
IES >= 0.72
or (R < 0.25 and I >= 0.60)
or (A >= 0.80 and RCS < 0.55)
```

### BLOCK

Select `BLOCK` when not suspended and:

```text
RAAS < 0.45
or RCS < 0.36
or (IES >= 0.62 and E < 0.65)
```

### CONSTRAIN

Select `CONSTRAIN` when not suspended or blocked and:

```text
RAAS < 0.74
or IES >= 0.36
or L >= 0.55
or A >= 0.35
```

### RELEASE

Select `RELEASE` only when none of the prior conditions apply.

## Enforcement Controls

| Decision | Controls |
| --- | --- |
| `RELEASE` | Execute action; retain reversal path. |
| `CONSTRAIN` | Reduce scope; precommit rollback plan; increase monitoring; cap blast radius when needed. |
| `BLOCK` | Block action; request reversal evidence; route for authorization review. |
| `SUSPEND` | Suspend action; isolate downstream effects; require explicit release approval. |

## Technical Effect

The mechanism does not merely score risk. It changes system execution based on reversibility-adjusted exposure. Two actions with similar base risk may receive different controls because one can be reversed and the other cannot.

## Design Rationale

Reversibility-weighted authorization is the primary technical mechanism in this reference design because it is:

- More technical than a broad governance claim.
- Directly tied to execution control.
- Easy to demonstrate in code.
- Commercially applicable across multiple industries.
- Specific enough to test against real action outcomes.
