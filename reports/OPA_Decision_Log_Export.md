# SMERC OPA-Style Decision Log Export

Generated: `2026-08-02T03:41:53+00:00`

## Summary

- Tenant: `pilot-review`
- Entries: `10`
- Posture counts: `{'ESCALATE': 4, 'THROTTLE': 3, 'FREEZE': 1, 'ALLOW': 2}`

## Interpretation

This export gives existing log pipelines an OPA-adjacent decision-log shape while preserving SMERC posture, recoverability scores, reason codes, controls, and replay IDs.

## Evidence Boundary

OPA-style export only. This is a compatibility shape for log pipelines; it is not OPA parity, Rego evaluation, or proof of production enforcement.
