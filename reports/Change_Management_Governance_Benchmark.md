# SMERC Change-Management-Inspired Governance Benchmark

Generated at: `2026-07-31T02:28:42+00:00`

## Purpose

This benchmark compares traditional change-management outcomes with SMERC recoverability-aware runtime postures for software delivery, infrastructure, and operations changes.

It does not test whether SMERC replaces change management. It tests whether recoverability scoring produces different runtime governance postures after a change has a familiar approval, CAB, emergency, or rejection label.

## Evidence Boundary

Change-management-inspired benchmark only. It is not ITIL certification, change-management software, ServiceNow/Jira replacement, CAB replacement, production approval, compliance attestation, customer validation, production certification, or incident-reduction proof.

## Summary

- Scenarios: `8`
- Traditional change counts: `{'APPROVE': 3, 'APPROVE_WITH_CAB': 3, 'EMERGENCY_APPROVE': 1, 'REJECT': 1}`
- SMERC posture counts: `{'ALLOW': 2, 'THROTTLE': 4, 'FREEZE': 0, 'DENY': 2, 'ESCALATE': 0}`
- Recoverability delta count: `7`
- Recoverability delta rate: `0.875`

## Delta Types

| Delta | Count | Meaning |
| --- | ---: | --- |
| `BOTH_APPROVE` | 1 | Both traditional change review and SMERC allow the action under the reference scenario. |
| `CHANGE_APPROVED_SMERC_RESTRAINT` | 6 | Traditional change review approves or emergency-approves the change, but SMERC restrains runtime execution because current recoverability, containment, rollback, evidence, or scope is weak. |
| `CHANGE_REJECTED_SMERC_NON_DENY` | 1 | Traditional change review rejects the change, while SMERC identifies a bounded runtime path such as constraint, escalation, or narrow release under the reference engine. |

## Scenario Results

| Scenario | Traditional Change | SMERC | Exposure | Capacity | Auth Score | Delta |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `CM_STANDARD_DEPENDENCY_PATCH` | `APPROVE` | `ALLOW` | 0.146 | 0.858 | 0.867 | `BOTH_APPROVE` |
| `CM_PRODUCTION_CANARY_DEPLOY` | `APPROVE_WITH_CAB` | `THROTTLE` | 0.385 | 0.72 | 0.712 | `CHANGE_APPROVED_SMERC_RESTRAINT` |
| `CM_EMERGENCY_SECURITY_PATCH_WIDE_SCOPE` | `EMERGENCY_APPROVE` | `THROTTLE` | 0.626 | 0.48 | 0.497 | `CHANGE_APPROVED_SMERC_RESTRAINT` |
| `CM_BROAD_IAM_PERMISSION_CHANGE` | `APPROVE_WITH_CAB` | `THROTTLE` | 0.768 | 0.404 | 0.403 | `CHANGE_APPROVED_SMERC_RESTRAINT` |
| `CM_DATABASE_MIGRATION_WEAK_ROLLBACK` | `APPROVE_WITH_CAB` | `DENY` | 0.813 | 0.343 | 0.37 | `CHANGE_APPROVED_SMERC_RESTRAINT` |
| `CM_FEATURE_FLAG_SAFE_RECOVERY` | `REJECT` | `ALLOW` | 0.123 | 0.891 | 0.846 | `CHANGE_REJECTED_SMERC_NON_DENY` |
| `CM_LOG_RETENTION_DELETION` | `APPROVE` | `DENY` | 0.808 | 0.267 | 0.307 | `CHANGE_APPROVED_SMERC_RESTRAINT` |
| `CM_INFRA_SCALE_UP_RECOVERABLE` | `APPROVE` | `THROTTLE` | 0.316 | 0.81 | 0.77 | `CHANGE_APPROVED_SMERC_RESTRAINT` |

## Demo-Ready Examples

### CM_DATABASE_MIGRATION_WEAK_ROLLBACK

- Category: `database_change`
- Traditional outcome: `APPROVE_WITH_CAB` because CAB approved after schema review and change-window scheduling, but rollback rehearsal is incomplete.
- SMERC posture: `DENY`
- Irreversible exposure score: `0.813`
- Reversible capacity score: `0.343`
- Reason codes: `['IRREVERSIBLE_EXPOSURE_HIGH', 'RECOVERY_CAPACITY_LOW', 'ROLLBACK_LATENCY_HIGH', 'CANCEL_RELIABILITY_WEAK', 'CONTAINMENT_WEAK', 'IMPACT_SCOPE_WIDE', 'EXTERNAL_SIDE_EFFECT', 'SENSITIVE_DATA']`
- Controls: `['block_execution', 'explain_denial', 'preserve_replay', 'require_new_request']`
- Interpretation: Traditional change review approves or emergency-approves the change, but SMERC restrains runtime execution because current recoverability, containment, rollback, evidence, or scope is weak.

### CM_LOG_RETENTION_DELETION

- Category: `evidence_change`
- Traditional outcome: `APPROVE` because Approved as a storage-cost reduction because the request matches a recurring cleanup task.
- SMERC posture: `DENY`
- Irreversible exposure score: `0.808`
- Reversible capacity score: `0.267`
- Reason codes: `['IRREVERSIBLE_EXPOSURE_HIGH', 'RECOVERY_CAPACITY_LOW', 'ROLLBACK_LATENCY_HIGH', 'CANCEL_RELIABILITY_WEAK', 'EVIDENCE_VALIDITY_LOW', 'ANOMALY_PRESSURE_HIGH', 'EXTERNAL_SIDE_EFFECT', 'SENSITIVE_DATA']`
- Controls: `['block_execution', 'explain_denial', 'preserve_replay', 'require_new_request']`
- Interpretation: Traditional change review approves or emergency-approves the change, but SMERC restrains runtime execution because current recoverability, containment, rollback, evidence, or scope is weak.

### CM_BROAD_IAM_PERMISSION_CHANGE

- Category: `identity_change`
- Traditional outcome: `APPROVE_WITH_CAB` because Change ticket includes manager approval and CAB approval for a broad IAM policy update.
- SMERC posture: `THROTTLE`
- Irreversible exposure score: `0.768`
- Reversible capacity score: `0.404`
- Reason codes: `['IRREVERSIBLE_EXPOSURE_HIGH', 'RECOVERY_CAPACITY_LOW', 'CONTAINMENT_WEAK', 'IMPACT_SCOPE_WIDE', 'EXTERNAL_SIDE_EFFECT', 'SENSITIVE_DATA']`
- Controls: `['limit_scope', 'preview_before_execution', 'record_replay', 'require_rollback_plan', 'rate_limit_external_side_effect', 'checkpoint_before_execution']`
- Interpretation: Traditional change review approves or emergency-approves the change, but SMERC restrains runtime execution because current recoverability, containment, rollback, evidence, or scope is weak.

### CM_EMERGENCY_SECURITY_PATCH_WIDE_SCOPE

- Category: `emergency_change`
- Traditional outcome: `EMERGENCY_APPROVE` because Emergency approval granted because the vulnerable package is exposed on a critical service.
- SMERC posture: `THROTTLE`
- Irreversible exposure score: `0.626`
- Reversible capacity score: `0.48`
- Reason codes: `['IRREVERSIBLE_EXPOSURE_ELEVATED', 'CONTAINMENT_WEAK', 'IMPACT_SCOPE_WIDE', 'EXTERNAL_SIDE_EFFECT']`
- Controls: `['limit_scope', 'preview_before_execution', 'record_replay', 'require_rollback_plan', 'rate_limit_external_side_effect', 'checkpoint_before_execution']`
- Interpretation: Traditional change review approves or emergency-approves the change, but SMERC restrains runtime execution because current recoverability, containment, rollback, evidence, or scope is weak.

### CM_PRODUCTION_CANARY_DEPLOY

- Category: `normal_change`
- Traditional outcome: `APPROVE_WITH_CAB` because CAB approved a canary deployment during the normal change window with service-owner signoff.
- SMERC posture: `THROTTLE`
- Irreversible exposure score: `0.385`
- Reversible capacity score: `0.72`
- Reason codes: `['EXTERNAL_SIDE_EFFECT']`
- Controls: `['limit_scope', 'preview_before_execution', 'record_replay', 'rate_limit_external_side_effect']`
- Interpretation: Traditional change review approves or emergency-approves the change, but SMERC restrains runtime execution because current recoverability, containment, rollback, evidence, or scope is weak.

## Commercial Interpretation

Change management is the familiar enterprise pattern for planning, approving, scheduling, reviewing, and documenting production changes. SMERC does not replace that discipline. It adds a pre-execution runtime question that change tickets often do not answer with enough precision: if this automated action is wrong, how fast and how completely can the organization recover?

For the GitHub Actions pilot, this gives a CISO or platform team a concrete way to inspect where an approved change still deserves constraints, where a rejected change may have a safe bounded path, and where evidence should be preserved for later replay.
