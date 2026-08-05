# SMERC Security-Response-Inspired Governance Benchmark

Generated at: `2026-07-31T02:34:37+00:00`

## Purpose

This benchmark compares security playbook outcomes with SMERC recoverability-aware runtime postures for AI-assisted security operations.

It does not test whether SMERC detects threats or replaces SOAR/SIEM/EDR tools. It tests whether recoverability scoring changes how automated response actions should proceed before they isolate systems, disable accounts, delete artifacts, notify customers, or alter controls.

## Evidence Boundary

Security-response-inspired benchmark only. It is not a SOAR platform, SIEM, EDR, incident-response service, malware classifier, threat-intelligence feed, compliance attestation, customer validation, production certification, or incident-reduction proof.

## Summary

- Scenarios: `8`
- Security playbook counts: `{'AUTO_EXECUTE': 4, 'ANALYST_REVIEW': 2, 'ESCALATE_INCIDENT': 1, 'DO_NOT_EXECUTE': 1}`
- SMERC posture counts: `{'ALLOW': 2, 'THROTTLE': 4, 'FREEZE': 0, 'DENY': 2, 'ESCALATE': 0}`
- Recoverability delta count: `4`
- Recoverability delta rate: `0.5`

## Delta Types

| Delta | Count | Meaning |
| --- | ---: | --- |
| `BOTH_AUTO_ALLOW` | 1 | Both the security playbook and SMERC allow automated execution under the reference scenario. |
| `BOTH_RESTRAIN` | 3 | Both lenses require restraint, but SMERC records recoverability scores, reason codes, and controls. |
| `PLAYBOOK_AUTO_SMERC_RESTRAINT` | 3 | The security playbook would auto-execute, but SMERC restrains the action because the proposed response could be hard to reverse, too broad, weakly evidenced, or poorly contained. |
| `PLAYBOOK_BLOCK_SMERC_BOUNDED_PATH` | 1 | The security playbook blocks execution, while SMERC identifies a bounded path such as throttled scope or escalation with replay evidence. |

## Scenario Results

| Scenario | Playbook | SMERC | Exposure | Capacity | Auth Score | Delta |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `SR_DISABLE_COMPROMISED_TEST_ACCOUNT` | `AUTO_EXECUTE` | `ALLOW` | 0.12 | 0.892 | 0.853 | `BOTH_AUTO_ALLOW` |
| `SR_QUARANTINE_EXECUTIVE_LAPTOP` | `AUTO_EXECUTE` | `THROTTLE` | 0.583 | 0.605 | 0.564 | `PLAYBOOK_AUTO_SMERC_RESTRAINT` |
| `SR_BLOCK_CUSTOMER_API_TOKEN_FLEET` | `AUTO_EXECUTE` | `THROTTLE` | 0.758 | 0.421 | 0.41 | `PLAYBOOK_AUTO_SMERC_RESTRAINT` |
| `SR_DELETE_SUSPECT_BUCKET_ARTIFACTS` | `AUTO_EXECUTE` | `DENY` | 0.817 | 0.308 | 0.336 | `PLAYBOOK_AUTO_SMERC_RESTRAINT` |
| `SR_FORCE_PASSWORD_RESET_TARGETED` | `ANALYST_REVIEW` | `THROTTLE` | 0.29 | 0.763 | 0.706 | `BOTH_RESTRAIN` |
| `SR_GLOBAL_FIREWALL_BLOCK` | `ESCALATE_INCIDENT` | `THROTTLE` | 0.69 | 0.44 | 0.449 | `BOTH_RESTRAIN` |
| `SR_SEND_CUSTOMER_BREACH_NOTICE` | `ANALYST_REVIEW` | `DENY` | 0.932 | 0.179 | 0.227 | `BOTH_RESTRAIN` |
| `SR_DISABLE_SUSPICIOUS_CI_SECRET` | `DO_NOT_EXECUTE` | `ALLOW` | 0.289 | 0.777 | 0.697 | `PLAYBOOK_BLOCK_SMERC_BOUNDED_PATH` |

## Demo-Ready Examples

### SR_DELETE_SUSPECT_BUCKET_ARTIFACTS

- Category: `cloud_forensics`
- Playbook outcome: `AUTO_EXECUTE` because Malware cleanup playbook removes artifacts matching known bad hashes from object storage.
- SMERC posture: `DENY`
- Irreversible exposure score: `0.817`
- Reversible capacity score: `0.308`
- Reason codes: `['IRREVERSIBLE_EXPOSURE_HIGH', 'RECOVERY_CAPACITY_LOW', 'ROLLBACK_LATENCY_HIGH', 'CANCEL_RELIABILITY_WEAK', 'ANOMALY_PRESSURE_HIGH', 'EXTERNAL_SIDE_EFFECT', 'SENSITIVE_DATA']`
- Controls: `['block_execution', 'explain_denial', 'preserve_replay', 'require_new_request']`
- Interpretation: The security playbook would auto-execute, but SMERC restrains the action because the proposed response could be hard to reverse, too broad, weakly evidenced, or poorly contained.

### SR_BLOCK_CUSTOMER_API_TOKEN_FLEET

- Category: `api_security`
- Playbook outcome: `AUTO_EXECUTE` because Token abuse playbook automatically revokes tokens associated with high-velocity suspicious calls.
- SMERC posture: `THROTTLE`
- Irreversible exposure score: `0.758`
- Reversible capacity score: `0.421`
- Reason codes: `['IRREVERSIBLE_EXPOSURE_HIGH', 'CANCEL_RELIABILITY_WEAK', 'ANOMALY_PRESSURE_HIGH', 'IMPACT_SCOPE_WIDE', 'EXTERNAL_SIDE_EFFECT', 'SENSITIVE_DATA']`
- Controls: `['limit_scope', 'preview_before_execution', 'record_replay', 'require_rollback_plan', 'rate_limit_external_side_effect', 'checkpoint_before_execution']`
- Interpretation: The security playbook would auto-execute, but SMERC restrains the action because the proposed response could be hard to reverse, too broad, weakly evidenced, or poorly contained.

### SR_QUARANTINE_EXECUTIVE_LAPTOP

- Category: `endpoint_containment`
- Playbook outcome: `AUTO_EXECUTE` because EDR rule recommends immediate quarantine after high-confidence malware detection.
- SMERC posture: `THROTTLE`
- Irreversible exposure score: `0.583`
- Reversible capacity score: `0.605`
- Reason codes: `['IRREVERSIBLE_EXPOSURE_ELEVATED', 'ANOMALY_PRESSURE_HIGH', 'EXTERNAL_SIDE_EFFECT', 'SENSITIVE_DATA']`
- Controls: `['limit_scope', 'preview_before_execution', 'record_replay', 'rate_limit_external_side_effect']`
- Interpretation: The security playbook would auto-execute, but SMERC restrains the action because the proposed response could be hard to reverse, too broad, weakly evidenced, or poorly contained.

### SR_SEND_CUSTOMER_BREACH_NOTICE

- Category: `external_communications`
- Playbook outcome: `ANALYST_REVIEW` because Customer notification requires legal, incident-command, and communications review.
- SMERC posture: `DENY`
- Irreversible exposure score: `0.932`
- Reversible capacity score: `0.179`
- Reason codes: `['IRREVERSIBLE_EXPOSURE_HIGH', 'RECOVERY_CAPACITY_LOW', 'ROLLBACK_LATENCY_HIGH', 'CANCEL_RELIABILITY_WEAK', 'CONTAINMENT_WEAK', 'EVIDENCE_VALIDITY_LOW', 'AUTHORIZATION_CONFIDENCE_LOW', 'IMPACT_SCOPE_WIDE', 'EXTERNAL_SIDE_EFFECT', 'SENSITIVE_DATA']`
- Controls: `['block_execution', 'explain_denial', 'preserve_replay', 'require_new_request']`
- Interpretation: Both lenses require restraint, but SMERC records recoverability scores, reason codes, and controls.

### SR_GLOBAL_FIREWALL_BLOCK

- Category: `network_containment`
- Playbook outcome: `ESCALATE_INCIDENT` because Potential command-and-control traffic requires incident escalation before a broad global block.
- SMERC posture: `THROTTLE`
- Irreversible exposure score: `0.69`
- Reversible capacity score: `0.44`
- Reason codes: `['IRREVERSIBLE_EXPOSURE_HIGH', 'CONTAINMENT_WEAK', 'ANOMALY_PRESSURE_HIGH', 'IMPACT_SCOPE_WIDE', 'EXTERNAL_SIDE_EFFECT']`
- Controls: `['limit_scope', 'preview_before_execution', 'record_replay', 'require_rollback_plan', 'rate_limit_external_side_effect', 'checkpoint_before_execution']`
- Interpretation: Both lenses require restraint, but SMERC records recoverability scores, reason codes, and controls.

## Commercial Interpretation

SOAR and incident-response programs are strongest at detection intake, enrichment, playbooks, analyst queues, and response execution. SMERC does not replace those systems. It adds a pre-execution recoverability checkpoint so automated security actions can be released, constrained, frozen, denied, or escalated based on blast radius and recovery capacity.

For a CISO, this is useful when security automation is moving from recommendation to action. The question is not only whether the alert is real. The question is whether the response action can be safely undone if the system is wrong.
