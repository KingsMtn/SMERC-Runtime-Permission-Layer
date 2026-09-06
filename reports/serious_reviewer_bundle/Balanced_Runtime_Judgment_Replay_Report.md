# Balanced Runtime Judgment Replay Report

Generated: `2026-09-06T22:24:17+00:00`
Version: `smerc.balanced-runtime-judgment-replay.v1`

## Work / Result / Impact

- Work: Run safe, borderline, uncertain, harmful, and escalation-worthy actions through the same SMERC evaluation path.
- Result: Evaluated 5 metadata-only records and compared expected postures with SMERC posture output.
- Impact: Reviewers can see whether SMERC demonstrates judgment across the whole posture ladder instead of acting like a simple blocker.

## Evidence Boundary

This replay proves local posture discrimination on curated metadata-only examples. It is not customer validation, production certification, a formal false-positive rate, or proof that thresholds are calibrated for a specific organization.

## Posture Distribution

- Expected posture counts: `{'ALLOW': 1, 'DENY': 1, 'ESCALATE': 1, 'FREEZE': 1, 'THROTTLE': 1}`
- SMERC posture counts: `{'ALLOW': 1, 'DENY': 1, 'ESCALATE': 1, 'FREEZE': 1, 'THROTTLE': 1}`
- Governance Routing Workbench route counts: `{'BLOCK': 1, 'CONSTRAINED_EXECUTE': 1, 'EXECUTE': 1, 'PAUSE': 1, 'REVIEW_REQUIRED': 1}`
- Valid DLL ledgers: `5`
- Delta counts: `{'MATCH': 5}`

## Decision Deltas

| Action | Expected posture | SMERC posture | Delta |
| --- | --- | --- | --- |
| `BALANCED_ALLOW_001` | `ALLOW` | `ALLOW` | `MATCH` |
| `BALANCED_THROTTLE_002` | `THROTTLE` | `THROTTLE` | `MATCH` |
| `BALANCED_FREEZE_003` | `FREEZE` | `FREEZE` | `MATCH` |
| `BALANCED_DENY_004` | `DENY` | `DENY` | `MATCH` |
| `BALANCED_ESCALATE_005` | `ESCALATE` | `ESCALATE` | `MATCH` |

## Reviewer Question

Which posture is most useful to tune first for your workflow: ALLOW, THROTTLE, FREEZE, DENY, or ESCALATE?
