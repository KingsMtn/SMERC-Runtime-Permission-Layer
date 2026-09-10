# SMERC Decision Language Conformance Report

Version: `smerc.decision-language-conformance.v1`
Status: `pass`
Decision count: `5`

## Work / Result / Impact

- Work: Check emitted decision JSON against the SMERC decision-language contract.
- Result: Checked 5 decision artifact(s) with 0 failure(s).
- Impact: Frameworks can adopt the SMERC posture vocabulary and evidence fields without adopting the full reference engine, while reviewers can still detect malformed or incomplete decisions.

## Summary

- Status counts: `{'pass': 5}`
- Posture counts: `{'ALLOW': 1, 'DENY': 1, 'ESCALATE': 1, 'FREEZE': 1, 'THROTTLE': 1}`

## Decisions

| Source | Posture | Status | Errors | Warnings |
| --- | --- | --- | --- | --- |
| `examples\decision_language\allow_decision.json` | `ALLOW` | `pass` | `[]` | `[]` |
| `examples\decision_language\throttle_decision.json` | `THROTTLE` | `pass` | `[]` | `[]` |
| `examples\decision_language\freeze_decision.json` | `FREEZE` | `pass` | `[]` | `[]` |
| `examples\decision_language\deny_decision.json` | `DENY` | `pass` | `[]` | `[]` |
| `examples\decision_language\escalate_decision.json` | `ESCALATE` | `pass` | `[]` | `[]` |

## Evidence Boundary

This conformance check validates the portable SMERC decision-language shape. It does not prove the underlying risk scores, production enforcement, customer calibration, or that route controls actually happened.
