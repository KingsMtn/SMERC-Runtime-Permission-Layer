# SMERC SRE Incident Governance Benchmark

Generated at: `2026-07-31T02:44:17+00:00`

## Purpose

This benchmark compares SRE incident playbook outcomes with SMERC recoverability-aware runtime postures for reliability automation.

It does not test whether SMERC replaces observability, incident management, SLOs, or pager workflows. It tests whether recoverability scoring changes how automated mitigations should proceed before they scale systems, roll back services, disable features, purge caches, alter traffic, or trigger failover.

## Evidence Boundary

SRE/incident-management-inspired benchmark only. It is not an observability platform, incident-management system, SLO calculator, pager routing service, production approval, customer validation, production certification, or incident-reduction proof.

## Summary

- Scenarios: `8`
- SRE playbook counts: `{'AUTO_MITIGATE': 4, 'MANUAL_APPROVAL': 1, 'INCIDENT_COMMAND': 2, 'HOLD': 1}`
- SMERC posture counts: `{'ALLOW': 1, 'THROTTLE': 6, 'FREEZE': 0, 'DENY': 1, 'ESCALATE': 0}`
- Recoverability delta count: `5`
- Recoverability delta rate: `0.625`

## Delta Types

| Delta | Count | Meaning |
| --- | ---: | --- |
| `BOTH_RESTRAIN` | 3 | Both lenses require restraint, but SMERC records recoverability scores, reason codes, and controls. |
| `SRE_AUTO_SMERC_RESTRAINT` | 4 | The SRE playbook would auto-mitigate, but SMERC restrains the action because rollback, containment, evidence, impact scope, or recovery capacity is not strong enough. |
| `SRE_HOLD_SMERC_BOUNDED_PATH` | 1 | The SRE playbook holds execution, while SMERC identifies a bounded path such as constrained mitigation or escalation with replay evidence. |

## Scenario Results

| Scenario | SRE Playbook | SMERC | Exposure | Capacity | Stress | Delta |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `SRE_SCALE_WORKERS_HIGH_LOAD` | `AUTO_MITIGATE` | `THROTTLE` | 0.291 | 0.811 | 0.298 | `SRE_AUTO_SMERC_RESTRAINT` |
| `SRE_GLOBAL_TRAFFIC_FAILOVER` | `AUTO_MITIGATE` | `THROTTLE` | 0.661 | 0.459 | 0.678 | `SRE_AUTO_SMERC_RESTRAINT` |
| `SRE_ROLLBACK_PAYMENT_SERVICE` | `INCIDENT_COMMAND` | `THROTTLE` | 0.377 | 0.752 | 0.437 | `BOTH_RESTRAIN` |
| `SRE_PURGE_CACHE_INCIDENT` | `AUTO_MITIGATE` | `THROTTLE` | 0.672 | 0.378 | 0.603 | `SRE_AUTO_SMERC_RESTRAINT` |
| `SRE_DISABLE_FEATURE_FLAG_TARGETED` | `MANUAL_APPROVAL` | `THROTTLE` | 0.201 | 0.868 | 0.254 | `BOTH_RESTRAIN` |
| `SRE_DELETE_QUEUE_BACKLOG` | `AUTO_MITIGATE` | `DENY` | 0.923 | 0.231 | 0.745 | `SRE_AUTO_SMERC_RESTRAINT` |
| `SRE_HOLD_DATABASE_FAILOVER_TEST` | `HOLD` | `ALLOW` | 0.138 | 0.824 | 0.22 | `SRE_HOLD_SMERC_BOUNDED_PATH` |
| `SRE_BROAD_RATE_LIMIT_CUSTOMERS` | `INCIDENT_COMMAND` | `THROTTLE` | 0.607 | 0.5 | 0.653 | `BOTH_RESTRAIN` |

## Demo-Ready Examples

### SRE_DELETE_QUEUE_BACKLOG

- Category: `data_loss_risk`
- SRE playbook outcome: `AUTO_MITIGATE` because Queue-drain playbook removes poison messages when retry storms threaten service recovery.
- SMERC posture: `DENY`
- Irreversible exposure score: `0.923`
- Reversible capacity score: `0.231`
- Operational stress score: `0.745`
- Reason codes: `['IRREVERSIBLE_EXPOSURE_HIGH', 'RECOVERY_CAPACITY_LOW', 'ROLLBACK_LATENCY_HIGH', 'CANCEL_RELIABILITY_WEAK', 'CONTAINMENT_WEAK', 'ANOMALY_PRESSURE_HIGH', 'IMPACT_SCOPE_WIDE', 'EXTERNAL_SIDE_EFFECT', 'SENSITIVE_DATA']`
- Controls: `['block_execution', 'explain_denial', 'preserve_replay', 'require_new_request']`
- Interpretation: The SRE playbook would auto-mitigate, but SMERC restrains the action because rollback, containment, evidence, impact scope, or recovery capacity is not strong enough.

### SRE_PURGE_CACHE_INCIDENT

- Category: `cache_mitigation`
- SRE playbook outcome: `AUTO_MITIGATE` because Stale content alert triggers a standard cache purge playbook.
- SMERC posture: `THROTTLE`
- Irreversible exposure score: `0.672`
- Reversible capacity score: `0.378`
- Operational stress score: `0.603`
- Reason codes: `['IRREVERSIBLE_EXPOSURE_ELEVATED', 'RECOVERY_CAPACITY_LOW', 'ROLLBACK_LATENCY_HIGH', 'CANCEL_RELIABILITY_WEAK', 'CONTAINMENT_WEAK', 'IMPACT_SCOPE_WIDE', 'EXTERNAL_SIDE_EFFECT']`
- Controls: `['limit_scope', 'preview_before_execution', 'record_replay', 'require_rollback_plan', 'rate_limit_external_side_effect', 'checkpoint_before_execution']`
- Interpretation: The SRE playbook would auto-mitigate, but SMERC restrains the action because rollback, containment, evidence, impact scope, or recovery capacity is not strong enough.

### SRE_GLOBAL_TRAFFIC_FAILOVER

- Category: `traffic_management`
- SRE playbook outcome: `AUTO_MITIGATE` because Regional health checks fail and traffic failover playbook is configured for automated mitigation.
- SMERC posture: `THROTTLE`
- Irreversible exposure score: `0.661`
- Reversible capacity score: `0.459`
- Operational stress score: `0.678`
- Reason codes: `['IRREVERSIBLE_EXPOSURE_ELEVATED', 'ANOMALY_PRESSURE_HIGH', 'IMPACT_SCOPE_WIDE', 'EXTERNAL_SIDE_EFFECT']`
- Controls: `['limit_scope', 'preview_before_execution', 'record_replay', 'require_rollback_plan', 'rate_limit_external_side_effect', 'checkpoint_before_execution']`
- Interpretation: The SRE playbook would auto-mitigate, but SMERC restrains the action because rollback, containment, evidence, impact scope, or recovery capacity is not strong enough.

### SRE_SCALE_WORKERS_HIGH_LOAD

- Category: `capacity_mitigation`
- SRE playbook outcome: `AUTO_MITIGATE` because CPU saturation and queue depth exceed thresholds and the standard autoscaling playbook is reversible.
- SMERC posture: `THROTTLE`
- Irreversible exposure score: `0.291`
- Reversible capacity score: `0.811`
- Operational stress score: `0.298`
- Reason codes: `['EXTERNAL_SIDE_EFFECT']`
- Controls: `['limit_scope', 'preview_before_execution', 'record_replay', 'rate_limit_external_side_effect']`
- Interpretation: The SRE playbook would auto-mitigate, but SMERC restrains the action because rollback, containment, evidence, impact scope, or recovery capacity is not strong enough.

### SRE_BROAD_RATE_LIMIT_CUSTOMERS

- Category: `traffic_shaping`
- SRE playbook outcome: `INCIDENT_COMMAND` because Customer-wide rate limiting requires incident-command approval due to business impact.
- SMERC posture: `THROTTLE`
- Irreversible exposure score: `0.607`
- Reversible capacity score: `0.5`
- Operational stress score: `0.653`
- Reason codes: `['IRREVERSIBLE_EXPOSURE_ELEVATED', 'ANOMALY_PRESSURE_HIGH', 'IMPACT_SCOPE_WIDE', 'EXTERNAL_SIDE_EFFECT']`
- Controls: `['limit_scope', 'preview_before_execution', 'record_replay', 'rate_limit_external_side_effect', 'checkpoint_before_execution']`
- Interpretation: Both lenses require restraint, but SMERC records recoverability scores, reason codes, and controls.

## Commercial Interpretation

SRE and incident-management systems are strongest at detection, alerting, ownership, mitigation playbooks, SLOs, incident command, and post-incident review. SMERC does not replace those systems. It adds an execution-time recoverability checkpoint before an automated mitigation changes production state.

For platform teams, this is useful when automation is asked to act during stress. The question is not only whether mitigation is urgent. The question is whether the mitigation itself is recoverable, bounded, and supported by enough evidence.
