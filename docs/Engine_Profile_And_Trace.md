# Engine Profiles And Decision Trace

SMERC's recoverability engine now emits profile, trace, and transition guidance fields for each decision.

The goal is not to make the engine more mysterious. The goal is to make decisions easier to inspect, challenge, calibrate, and improve.

## Domain Profiles

Domain profiles adjust the reference recoverability scoring for common operating environments while preserving the same posture model.

Available profiles:

| Profile | Intended Use |
| --- | --- |
| `general` | Default reference behavior |
| `github_actions` | CI/CD, code, and deployment workflows |
| `cloud_admin` | Cloud infrastructure and control-plane actions |
| `finance_ops` | Payments, transfers, refunds, treasury, and finance workflows |
| `security_ops` | Security automation, containment, detection, and response |
| `customer_comms` | Customer-facing messages and irreversible communications |
| `it_ops` | Identity, endpoint, and internal IT operations |

Profiles can be selected per action:

```json
{
  "context": {
    "domain_profile": "finance_ops"
  }
}
```

If no profile is supplied, SMERC uses `general`.

## Decision Trace

Each decision includes:

```json
{
  "domain_profile": {
    "profile_id": "finance_ops",
    "label": "Finance operations",
    "notes": ["Money movement and payment workflows require stronger recovery evidence."]
  },
  "decision_trace": {
    "profile": {},
    "score_contributions": {},
    "threshold_trace": []
  },
  "transition_guidance": {}
}
```

### Score Contributions

`score_contributions` shows how each score was assembled before the posture decision:

- irreversible exposure
- reversible capacity
- confidence
- operational stress
- risk-adjusted authorization

Each score includes component values, the profile multiplier, and the final rounded total.

### Threshold Trace

`threshold_trace` shows which posture rules were evaluated and whether each triggered:

- deny by exposure plus low recovery or low confidence
- deny by unreliable cancellation plus high exposure
- escalate by operational stress
- freeze by low confidence or low capacity
- throttle by low authorization, elevated exposure, or external side effect

The trace is intended for audit, review, and calibration. It is not a promise that the default thresholds are correct for every enterprise.

## Transition Guidance

`transition_guidance` explains what would help move a decision toward a less restrictive posture.

It includes:

- current posture
- target posture
- release conditions
- blocking factors
- evidence needed
- control improvements

Example uses:

- A `DENY` decision can show that rollback evidence and stronger containment are needed before a future request could become `THROTTLE`.
- A `THROTTLE` decision can show what controls would need to improve before `ALLOW`.
- A reviewer can compare the guidance with real operational controls.

## Important Limits

Profiles are reference calibrations, not validated production thresholds.

The trace explains the current engine's reasoning. It does not prove that the reasoning is correct for every organization, workflow, or regulatory environment.

Design partners should compare profile output with reviewer agreement, false releases, false constraints, latency, and incident-review evidence before enforcement.
