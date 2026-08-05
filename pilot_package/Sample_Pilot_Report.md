# SMERC Sample Pilot Report

## Report Status

This is a sample report template. Values below are illustrative and must be replaced with customer pilot data before use.

## Executive Summary

SMERC was evaluated in shadow mode against an in-scope automation workflow. The pilot measured whether recoverability-aware posture decisions provided useful governance signal compared with existing review and allow/deny controls.

The pilot did not replace existing approvals, did not block production workflows, and did not process raw secrets or customer payloads.

## Pilot Scope

| Field | Value |
| --- | --- |
| Customer | Example customer |
| Workflow | GitHub Actions deployment workflow |
| Pilot mode | Observe |
| Duration | 30 days |
| Actions evaluated | 125 |
| Reviewers | Security and platform reviewers |
| Data boundary | Metadata-only |

## Decision Summary

| Posture | Count | Percentage | Notes |
| --- | ---: | ---: | --- |
| `ALLOW` | 52 | 41.6% | Low-risk, recoverable actions |
| `THROTTLE` | 48 | 38.4% | Required constraints or added review |
| `FREEZE` | 12 | 9.6% | Missing evidence or instability |
| `DENY` | 5 | 4.0% | Not structurally defensible |
| `ESCALATE` | 8 | 6.4% | Required higher-authority review |

## Reviewer Metrics

| Metric | Result | Interpretation |
| --- | ---: | --- |
| Reviewer agreement rate | 78% | Initial evidence of understandable recommendations |
| Useful constraint rate | 46% | Constraints were sometimes actionable |
| False release candidate rate | 3% | Requires review before enforcement |
| False constraint candidate rate | 14% | Indicates tuning needed |
| Median added review latency | 2 minutes | Within pilot tolerance |

## Most Useful Findings

1. SMERC identified production deployment actions where rollback latency made normal approval insufficient.
2. `THROTTLE` recommendations were more useful than simple blocking for medium-risk workflow changes.
3. Missing evidence and unclear rollback paths were recurring drivers of `FREEZE`.
4. Reviewers wanted clearer mapping from reason codes to existing controls.

## Representative Decisions

### Decision 1

- Replay ID: `example-replay-001`
- Action: production configuration deployment
- SMERC posture: `THROTTLE`
- Reviewer label: agree
- Reason codes: rollback latency elevated, impact scope high
- Useful controls: require change window, limit blast radius, confirm rollback

### Decision 2

- Replay ID: `example-replay-002`
- Action: delete old workflow artifact bucket
- SMERC posture: `FREEZE`
- Reviewer label: agree
- Reason codes: low reversibility, insufficient evidence
- Outcome: action paused until owner confirmed backup and retention policy

### Decision 3

- Replay ID: `example-replay-003`
- Action: run unit tests on feature branch
- SMERC posture: `ALLOW`
- Reviewer label: agree
- Reason codes: low risk, high reversibility, no external side effect

## Integration Issues

- Some action metadata required manual mapping.
- Workflow owner needed clearer guidance for rollback latency scoring.
- Existing approvals did not expose enough information about containment strength.
- Reason-code display should be improved before recommend mode.

## Recommendation

Recommended next step:

Move from observe mode to recommend mode for the same workflow for another 30 days.

Do not move to production enforcement yet. Enforcement should wait until:

- false release candidates are reviewed and reduced
- reason-code-to-control mapping is accepted by reviewers
- metadata generation is automated
- security owner approves limited enforcement criteria

## Evidence Boundary

This report is pilot evidence only. It does not prove production incident reduction, compliance readiness, or universal model accuracy.
