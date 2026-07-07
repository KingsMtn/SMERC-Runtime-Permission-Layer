# SMERC Policy Language v0

## Status

`smerc.spl.v0` is a starter policy-language profile for controlled pilots. It is not yet a full production policy language with grammar tooling, package management, IDE support, or formal verification.

The purpose of SPL v0 is practical:

> Let a reviewer describe runtime posture thresholds in a human-oriented document and compile that document into the existing `smerc.policy.v1` runtime contract.

## Why SPL Exists

SMERC decisions should not depend on hidden constants or prose. A design partner needs to inspect:

- what tenant the policy applies to
- what mode the policy is allowed to run in
- what evidence ceiling limits deployment
- what thresholds drive throttle, freeze, deny, and escalate behavior
- who approved the policy
- when the policy becomes effective
- what deterministic hash identifies the compiled policy

SPL v0 keeps those fields readable while preserving the stricter runtime policy contract already used by the engine.

## Compilation Boundary

```text
smerc.spl.v0 JSON -> reference_engine.spl.compile_spl -> smerc.policy.v1 JSON -> runtime engine
```

The compiler rejects:

- unknown fields
- missing fields
- unsupported versions
- incoherent threshold ordering
- `ENFORCE` policies without `fail_closed`
- modes that exceed the admitted evidence ceiling
- malformed runtime identifiers and timestamps

The final validation is performed by `RuntimePolicy.from_dict`, so SPL cannot bypass the existing policy safety checks.

## SPL Shape

```json
{
  "version": "smerc.spl.v0",
  "tenant": {
    "id": "platform-team"
  },
  "policy": {
    "id": "github-actions-shadow-mode",
    "revision": "2026.07.07",
    "mode": "OBSERVE",
    "fail_behavior": "report_unavailable",
    "approved_by_role": "security-architecture-review",
    "effective_at": "2026-07-07T00:00:00Z"
  },
  "evidence": {
    "program_id": "smerc-core-validation-v1",
    "ceiling": "OBSERVE"
  },
  "thresholds": {
    "throttle": {
      "authorization_min": 0.62,
      "exposure_min": 0.45
    },
    "freeze": {
      "confidence_max": 0.45,
      "capacity_max": 0.36
    },
    "deny": {
      "exposure_min": 0.78,
      "capacity_max": 0.42,
      "confidence_max": 0.48,
      "cancel_reliability_max": 0.30,
      "cancel_exposure_min": 0.62
    },
    "escalate": {
      "stress_min": 0.70
    }
  }
}
```

## Modes

| Mode | Meaning |
| --- | --- |
| `OBSERVE` | Score and record decisions without recommending or enforcing workflow changes. |
| `RECOMMEND` | Surface posture guidance and controls for reviewer use. |
| `ENFORCE` | Permit eligible execution or fail/route selected postures, subject to evidence ceiling. |

## Evidence Ceilings

| Ceiling | Maximum Allowed Mode |
| --- | --- |
| `STOP` | `OBSERVE` |
| `OBSERVE` | `OBSERVE` |
| `RECOMMEND` | `RECOMMEND` |
| `LIMITED_ENFORCE` | `ENFORCE` |
| `CALIBRATED_ENFORCE` | `ENFORCE` |

Evidence ceilings prevent a policy from silently becoming more forceful than the admitted evidence supports.

## Compile Commands

Compile and pretty-print:

```bash
python -m reference_engine.spl examples/policies/github_actions_shadow_spl.json --pretty
```

Print the deterministic compiled policy hash:

```bash
python -m reference_engine.spl examples/policies/github_actions_shadow_spl.json --hash
```

The compiled output is a strict `smerc.policy.v1` object that can be loaded through `PolicyRegistry.from_directory`.

## Current Limits

SPL v0 is intentionally narrow. It does not yet include:

- a custom text grammar
- comments or imports
- reusable rule blocks
- organization-wide inheritance
- IDE syntax highlighting
- static analysis beyond runtime-policy validation
- policy simulation reports
- policy signing or approval workflow

Those are candidates for later versions after design-partner feedback confirms which policy surface buyers actually need.

