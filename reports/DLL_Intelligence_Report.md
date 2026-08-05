# SMERC DLL Intelligence Report

Generated: `2026-07-18T03:46:17+00:00`

## Executive Summary

DLL Intelligence analyzed `6` verified lifecycle ledger(s), found `4` near-miss decision(s), `1` recovery failure(s), and `15` policy-review queue item(s).

This is governance intelligence built from lifecycle evidence. It is not automatic policy activation.

## Core Metrics

- Human reviewed: `6`
- Override rate: `0.167`
- Helpful overrides: `0`
- Harmful overrides: `1`
- Rollback success rate: `1.0`
- Judged-correct rate: `0.833`
- Unexpected consequence rate: `0.167`
- Controls sufficient rate: `0.833`
- Initial postures: `{'ALLOW': 1, 'DENY': 1, 'ESCALATE': 1, 'FREEZE': 1, 'THROTTLE': 2}`
- Final postures: `{'ALLOW': 1, 'DENY': 1, 'FREEZE': 1, 'THROTTLE': 3}`

## Recurring Signals

- Top reason codes: `{'EVIDENCE_INCOMPLETE': 3, 'RECOVERY_PATH_PARTIAL': 2, 'LOW_IMPACT': 1, 'RECOVERY_PATH_STRONG': 1, 'IMPACT_SCOPE_ELEVATED': 1, 'IRREVERSIBLE_EXPOSURE_HIGH': 1, 'FINANCIAL_IMPACT_HIGH': 1, 'ANOMALY_PRESSURE_ELEVATED': 1, 'AUTHORITY_CHANGE_HIGH': 1}`
- Top missing evidence: `{'rollback_drill': 3, 'human_approval': 1, 'backup_verification': 1, 'dual_approval': 1, 'customer_entitlement_proof': 1, 'owner_confirmation': 1}`
- Top safeguards: `{'canary_only': 2, 'record_decision': 1, 'retain_rollback_plan': 1, 'block_execution': 1, 'require_data_owner_review': 1, 'dual_approval': 1, 'transaction_limit': 1, 'automatic_rollback': 1, 'pause_automation': 1, 'require_owner_confirmation': 1}`

## Near-Miss Decisions

- `dll_pilot_002_canary_deploy`: Deploy generated API change to canary. -> `THROTTLE`
- `dll_pilot_003_delete_customer_table`: Delete a customer table after ambiguous cleanup request. -> `DENY`
- `dll_pilot_005_failed_deploy_rollback`: Apply infrastructure autoscaling change. -> `THROTTLE`
- `dll_pilot_006_security_key_rotation`: Rotate production signing key without owner confirmation. -> `FREEZE`

## Policy Review Queue

- `policy_update`: Review posture threshold for read_only_reporting. (`requires_review`)
- `rule_modification`: Map recurring controls for read_only_reporting actions. (`requires_review`)
- `policy_update`: Review posture threshold for github_actions_deployment. (`requires_review`)
- `rule_modification`: Map recurring controls for github_actions_deployment actions. (`requires_review`)
- `policy_update`: Review posture threshold for data_destruction. (`requires_review`)
- `rule_modification`: Map recurring controls for data_destruction actions. (`requires_review`)
- `policy_update`: Review posture threshold for finance_operations. (`requires_review`)
- `rule_modification`: Map recurring controls for finance_operations actions. (`requires_review`)
- `policy_update`: Review posture threshold for cloud_administration. (`requires_review`)
- `rule_modification`: Map recurring controls for cloud_administration actions. (`requires_review`)
- `policy_update`: Review posture threshold for security_operations. (`requires_review`)
- `rule_modification`: Map recurring controls for security_operations actions. (`requires_review`)
- `recurring_missing_evidence`: Require or explain missing evidence item: rollback_drill (`requires_review`)
- `recurring_reason_code`: Review policy threshold or control mapping for reason code: EVIDENCE_INCOMPLETE (`requires_review`)
- `recurring_reason_code`: Review policy threshold or control mapping for reason code: RECOVERY_PATH_PARTIAL (`requires_review`)

## Governance Drift Signals

- `unexpected_consequences_above_10_percent_of_outcome_reviewed_actions`

## Evidence Boundary

- DLL Intelligence summarizes supplied lifecycle records; it does not prove incident reduction by itself.
- Synthetic or analyst-assigned ledgers must be labeled before external use.
- Policy and calibration recommendations require human review before activation.

## Recommended Next Action

Collect at least 30 customer-context DLL records before presenting rates as pilot evidence.
