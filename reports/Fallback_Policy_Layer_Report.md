# SMERC Fallback Policy Layer Report

- Generated: `2026-08-26T20:52:33+00:00`
- Scenarios evaluated: `5`
- Fallback applied: `4`
- Fallback posture counts: `{'ALLOW': 1, 'DENY': 2, 'FREEZE': 2}`

| Action | Class | Proposed | Fallback | Failure | High Impact | Reasons |
| --- | --- | --- | --- | --- | --- | --- |
| FALLBACK_SAFE_TEST_001 | run_tests | ALLOW | ALLOW | none | False | FALLBACK_NOT_APPLIED |
| FALLBACK_SCANNER_DOWN_002 | delete_data | THROTTLE | FREEZE | content_scanner_unavailable | True | FALLBACK_CONTENT_SCANNER_UNAVAILABLE, FALLBACK_FAILURE_CONTENT_SCANNER_UNAVAILABLE |
| FALLBACK_STALE_POLICY_003 | modify_production | ALLOW | FREEZE | policy_bundle_stale | True | FALLBACK_FAILURE_POLICY_BUNDLE_STALE, FALLBACK_POLICY_STALE |
| FALLBACK_NO_ROLLBACK_004 | move_money | THROTTLE | DENY | rollback_plan_missing | True | FALLBACK_FAILURE_ROLLBACK_PLAN_MISSING, FALLBACK_LOW_RECOVERY_HIGH_EXPOSURE, FALLBACK_ROLLBACK_PLAN_MISSING_FOR_HIGH_IMPACT |
| FALLBACK_REVIEW_DOWN_005 | security_response | FREEZE | DENY | review_queue_unavailable | True | FALLBACK_FAILURE_REVIEW_QUEUE_UNAVAILABLE, FALLBACK_REVIEW_QUEUE_UNAVAILABLE_FOR_HELD_HIGH_IMPACT_ACTION |

## Evidence Boundary

Synthetic fallback examples demonstrate deterministic failure handling, not production validation.

