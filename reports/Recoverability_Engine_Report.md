# SMERC Recoverability Engine Report

Generated: `2026-07-03T04:22:15.042078+00:00`

## Summary

- Actions evaluated: `5`
- Non-release rate: `0.8`
- Average irreversible exposure: `0.562`
- Average reversible capacity: `0.516`
- Average authorization score: `0.532`

## Posture Distribution

| Posture | Count |
| --- | ---: |
| `ALLOW` | 1 |
| `THROTTLE` | 2 |
| `FREEZE` | 1 |
| `DENY` | 1 |
| `ESCALATE` | 0 |

## Action Decisions

| Action | Posture | Enforcement | Exposure | Capacity | Authorization | Reason Codes |
| --- | --- | --- | ---: | ---: | ---: | --- |
| AGENT_RUN_TESTS | `ALLOW` | `release` | 0.077 | 0.918 | 0.917 | RECOVERABILITY_ACCEPTABLE |
| AGENT_DEPLOY_PROD_CONFIG | `THROTTLE` | `constrain` | 0.502 | 0.588 | 0.595 | IRREVERSIBLE_EXPOSURE_ELEVATED, EXTERNAL_SIDE_EFFECT |
| AGENT_DELETE_AUDIT_LOGS | `FREEZE` | `pause` | 0.717 | 0.292 | 0.337 | IRREVERSIBLE_EXPOSURE_HIGH, RECOVERY_CAPACITY_LOW, ROLLBACK_LATENCY_HIGH, CONTAINMENT_WEAK, EVIDENCE_VALIDITY_LOW, AUTHORIZATION_CONFIDENCE_LOW, EXTERNAL_SIDE_EFFECT |
| AGENT_EXPORT_CUSTOMER_DATA | `DENY` | `block` | 0.874 | 0.23 | 0.264 | IRREVERSIBLE_EXPOSURE_HIGH, RECOVERY_CAPACITY_LOW, ROLLBACK_LATENCY_HIGH, CANCEL_RELIABILITY_WEAK, CONTAINMENT_WEAK, AUTHORIZATION_CONFIDENCE_LOW, ANOMALY_PRESSURE_HIGH, IMPACT_SCOPE_WIDE, EXTERNAL_SIDE_EFFECT, SENSITIVE_DATA |
| AGENT_ROTATE_SECRET | `THROTTLE` | `constrain` | 0.638 | 0.554 | 0.547 | IRREVERSIBLE_EXPOSURE_ELEVATED, IMPACT_SCOPE_WIDE, EXTERNAL_SIDE_EFFECT, SENSITIVE_DATA |

## Product Interpretation

This report demonstrates SMERC as a recoverability-aware pre-execution decision layer. In a real pilot, each non-release decision should be compared against human reviewer judgment, existing policy outcomes, overrides, and operational latency.
