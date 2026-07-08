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

## Custom Profiles

Design partners can load strict custom profiles without editing engine code.

Custom profiles use `smerc.domain_profile.v1` and are validated with exact fields. Unknown fields, missing fields, invalid multipliers, duplicate IDs, and unsafe identifiers are rejected.

Example:

```json
{
  "version": "smerc.domain_profile.v1",
  "profile_id": "github_actions_strict",
  "label": "GitHub Actions strict deployment profile",
  "exposure_multiplier": 1.08,
  "capacity_multiplier": 0.95,
  "confidence_multiplier": 0.98,
  "stress_multiplier": 1.08,
  "authorization_multiplier": 0.96,
  "allow_external_side_effect_without_throttle": false,
  "notes": [
    "Tuned for shadow-mode review of production deployment and infrastructure workflows."
  ]
}
```

Run the CLI with a single profile file:

```bash
python -m reference_engine.recoverability_engine \
  examples/recoverability_single_action.json \
  --domain-profile-file examples/domain_profiles/github_actions_strict.json \
  --domain-profile github_actions_strict \
  --pretty
```

Run the API with a directory of approved profiles:

```bash
python api_server.py \
  --host 127.0.0.1 \
  --port 8788 \
  --audit-db :memory: \
  --allow-unauthenticated \
  --domain-profile-dir examples/domain_profiles
```

The same setting can be supplied with `SMERC_DOMAIN_PROFILE_DIR`.

Schema:

- `schemas/smerc-domain-profile-v1.schema.json`

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
