# SMERC Operator Status Report

Generated: `2026-08-02T03:09:27+00:00`

## Status

- Tenant: `pilot-review`
- Operator status: `ready_for_review`
- Active policy version: `smerc.policy.reference`
- Active profile version: `github_actions_strict`

## Readiness

- Pilot ready for week zero: `true`
- Pilot ready for customer observe: `true`
- Customer ready for review call: `true`
- Customer ready for week zero: `false`

## Decision Activity

- Decision count: `10`
- Posture counts: `{'ALLOW': 2, 'THROTTLE': 3, 'FREEZE': 1, 'DENY': 0, 'ESCALATE': 4, 'UNAVAILABLE': 0}`
- Unavailable count: `0`
- Unavailable rate: `0.0`
- Top reason codes: `[('EXTERNAL_SIDE_EFFECT', 8), ('HIGH_HARM_POTENTIAL', 5), ('SENSITIVE_DATA_ACCESS', 4), ('LOW_REVERSIBILITY', 4), ('MODERATE_HARM_POTENTIAL', 3), ('CONSENT_OR_AUTHORIZATION_WEAK', 3), ('CONFIDENCE_SCORE_LOW', 3), ('RISK_SCORE_HIGH', 2), ('LOW_RISK_REPLAYABLE_ACTION', 2), ('LOW_MODEL_CONFIDENCE', 1)]`
- Top controls: `[('preserve_replay', 5), ('log_replay', 5), ('route_to_human_review', 4), ('require_explicit_approval', 4), ('limit_scope', 3), ('preview_before_execution', 3), ('rate_limit_external_effect', 3), ('execute', 2), ('require_recovery_path', 2), ('pause_execution', 1)]`

## Operational Checks

| Check | Status | Detail |
| --- | --- | --- |
| `policy_version_declared` | `ready` | Active policy version is included in the operator report. |
| `profile_version_declared` | `ready` | Active domain/profile version is included in the operator report. |
| `pilot_readiness` | `ready` | Week-zero readiness is generated from the GitHub Actions pilot readiness report. |
| `customer_intake` | `ready` | Customer intake must be ready for a review call before pilot setup. |
| `decision_artifacts` | `ready` | Decision artifacts are present for operator distribution and log export. |

## Evidence Boundary

Operator status summarizes pilot artifacts and readiness reports. It does not prove production availability, incident reduction, compliance, or customer validation.
