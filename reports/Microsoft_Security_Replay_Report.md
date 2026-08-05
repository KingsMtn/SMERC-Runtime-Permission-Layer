# SMERC Microsoft-Style Security Replay Report

Generated at: `2026-08-05T02:14:14+00:00`

## Purpose

This replay shows how SMERC can evaluate proposed automated responses derived from Microsoft Sentinel, Defender, Azure Activity, and advanced-hunting style events before execution.

It does not test Microsoft detection quality. It tests whether recoverability scoring changes the runtime posture of the next automated response action.

## Evidence Boundary

Microsoft-style replay based on public schema concepts and synthetic sample events only. This is not Microsoft telemetry, Microsoft certification, Sentinel validation, Defender validation, customer validation, threat detection, incident reduction proof, or a replacement for Microsoft security tools.

## Summary

- Events: `6`
- Event sources: `{'advanced_hunting_event': 1, 'azure_activity_log': 1, 'microsoft_defender_alert': 2, 'microsoft_sentinel_incident': 2}`
- Microsoft-style workflow counts: `{'ALERT_ONLY': 0, 'ANALYST_REVIEW': 2, 'AUTO_RESPONSE': 3, 'DO_NOT_EXECUTE': 0, 'ESCALATE_INCIDENT': 1}`
- SMERC posture counts: `{'ALLOW': 1, 'THROTTLE': 5, 'FREEZE': 0, 'DENY': 0, 'ESCALATE': 0}`
- Decision difference count: `5`
- Decision difference rate: `0.833`
- Auto responses restrained by SMERC: `2`
- Review/escalation events with bounded SMERC path: `3`
- Average exposure by source: `{'advanced_hunting_event': 0.657, 'azure_activity_log': 0.521, 'microsoft_defender_alert': 0.427, 'microsoft_sentinel_incident': 0.578}`

## Delta Types

| Delta | Count | Meaning |
| --- | ---: | --- |
| `BOTH_ALLOW` | 1 | Both the Microsoft-style workflow and SMERC allow automated execution under the sample metadata. |
| `MICROSOFT_AUTO_SMERC_RESTRAINT` | 2 | A Microsoft-style workflow would auto-respond, while SMERC restrains the action because runtime recoverability, containment, rollback latency, evidence, or impact scope warrants additional controls. |
| `MICROSOFT_REVIEW_SMERC_BOUNDED` | 3 | A Microsoft-style workflow would queue or escalate the event, while SMERC identifies a bounded runtime path that may be allowed or throttled with evidence and controls. |

## Replay Results

| Event | Source | Microsoft-Style Workflow | SMERC | Exposure | Capacity | Delta |
| --- | --- | --- | --- | ---: | ---: | --- |
| `msft-style-defender-001` | `microsoft_defender_alert` | `AUTO_RESPONSE` | `THROTTLE` | 0.605 | 0.637 | `MICROSOFT_AUTO_SMERC_RESTRAINT` |
| `msft-style-sentinel-002` | `microsoft_sentinel_incident` | `ANALYST_REVIEW` | `THROTTLE` | 0.512 | 0.679 | `MICROSOFT_REVIEW_SMERC_BOUNDED` |
| `msft-style-defender-003` | `microsoft_defender_alert` | `AUTO_RESPONSE` | `ALLOW` | 0.25 | 0.752 | `BOTH_ALLOW` |
| `msft-style-activity-004` | `azure_activity_log` | `AUTO_RESPONSE` | `THROTTLE` | 0.521 | 0.637 | `MICROSOFT_AUTO_SMERC_RESTRAINT` |
| `msft-style-hunting-005` | `advanced_hunting_event` | `ANALYST_REVIEW` | `THROTTLE` | 0.657 | 0.542 | `MICROSOFT_REVIEW_SMERC_BOUNDED` |
| `msft-style-sentinel-006` | `microsoft_sentinel_incident` | `ESCALATE_INCIDENT` | `THROTTLE` | 0.644 | 0.585 | `MICROSOFT_REVIEW_SMERC_BOUNDED` |

## Demo-Ready Examples

### msft-style-hunting-005: Mass mailbox forwarding rule creation

- Source: `advanced_hunting_event`
- Severity: `medium`
- Proposed response: Remove suspicious forwarding rules from 42 mailboxes
- Microsoft-style workflow: `ANALYST_REVIEW` because Mailbox rule removal affects users and is normally queued for analyst confirmation.
- SMERC posture: `THROTTLE`
- Reason codes: `['IRREVERSIBLE_EXPOSURE_ELEVATED', 'ANOMALY_PRESSURE_HIGH', 'IMPACT_SCOPE_WIDE', 'EXTERNAL_SIDE_EFFECT', 'SENSITIVE_DATA']`
- Controls: `['limit_scope', 'preview_before_execution', 'record_replay', 'rate_limit_external_side_effect', 'checkpoint_before_execution']`
- Interpretation: A Microsoft-style workflow would queue or escalate the event, while SMERC identifies a bounded runtime path that may be allowed or throttled with evidence and controls.

### msft-style-sentinel-006: Suspected data exfiltration to newly registered domain

- Source: `microsoft_sentinel_incident`
- Severity: `high`
- Proposed response: Block egress to suspected exfiltration domain across enterprise network controls
- Microsoft-style workflow: `ESCALATE_INCIDENT` because High-severity data exfiltration triggers incident escalation before network-wide changes.
- SMERC posture: `THROTTLE`
- Reason codes: `['IRREVERSIBLE_EXPOSURE_ELEVATED', 'ANOMALY_PRESSURE_HIGH', 'IMPACT_SCOPE_WIDE', 'EXTERNAL_SIDE_EFFECT', 'SENSITIVE_DATA']`
- Controls: `['limit_scope', 'preview_before_execution', 'record_replay', 'require_rollback_plan', 'rate_limit_external_side_effect', 'checkpoint_before_execution']`
- Interpretation: A Microsoft-style workflow would queue or escalate the event, while SMERC identifies a bounded runtime path that may be allowed or throttled with evidence and controls.

### msft-style-defender-001: Suspicious remote execution on executive laptop

- Source: `microsoft_defender_alert`
- Severity: `high`
- Proposed response: Isolate executive laptop from the network before analyst confirmation
- Microsoft-style workflow: `AUTO_RESPONSE` because Endpoint containment policy would isolate the device automatically for high-severity lateral-movement behavior.
- SMERC posture: `THROTTLE`
- Reason codes: `['IRREVERSIBLE_EXPOSURE_ELEVATED', 'ANOMALY_PRESSURE_HIGH', 'EXTERNAL_SIDE_EFFECT', 'SENSITIVE_DATA']`
- Controls: `['limit_scope', 'preview_before_execution', 'record_replay', 'require_rollback_plan', 'rate_limit_external_side_effect']`
- Interpretation: A Microsoft-style workflow would auto-respond, while SMERC restrains the action because runtime recoverability, containment, rollback latency, evidence, or impact scope warrants additional controls.

### msft-style-activity-004: Unexpected network security group rule opened to internet

- Source: `azure_activity_log`
- Severity: `high`
- Proposed response: Remove public network security group rule across affected subscriptions
- Microsoft-style workflow: `AUTO_RESPONSE` because Cloud guardrail would revert the rule automatically because it exposes a sensitive service.
- SMERC posture: `THROTTLE`
- Reason codes: `['IRREVERSIBLE_EXPOSURE_ELEVATED', 'ANOMALY_PRESSURE_HIGH', 'EXTERNAL_SIDE_EFFECT']`
- Controls: `['limit_scope', 'preview_before_execution', 'record_replay', 'require_rollback_plan', 'rate_limit_external_side_effect']`
- Interpretation: A Microsoft-style workflow would auto-respond, while SMERC restrains the action because runtime recoverability, containment, rollback latency, evidence, or impact scope warrants additional controls.

## Commercial Interpretation

Microsoft Sentinel, Defender, Entra, and Azure controls are strong at detection, identity, telemetry, workflow, and response execution. SMERC does not replace them. The commercial question is whether security and platform teams want a recoverability-aware checkpoint before an automated response creates business side effects.

The practical first pilot would run in shadow mode: export Microsoft-style alert or incident metadata, map the proposed response action, let SMERC score the action, and compare SMERC posture with the existing workflow outcome. No production blocking or private telemetry is required for the first review.
