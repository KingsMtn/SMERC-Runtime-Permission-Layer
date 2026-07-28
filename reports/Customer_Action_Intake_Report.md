# ExampleCo Customer Action Intake Report

Generated at: `2026-07-28T02:29:45+00:00`
Contact role: `security_architect`

## Evidence Boundary

Customer action intake is metadata-only pilot preparation. It is not proof of production safety, customer demand, or incident reduction.

## Workflow Context

Candidate AI-agent and automation actions for a GitHub Actions shadow-mode pilot.

## Summary

- Total actions: `6`
- Posture counts: `{'ALLOW': 1, 'THROTTLE': 4, 'FREEZE': 0, 'DENY': 1, 'ESCALATE': 0}`
- Domain profiles: `{'cloud_admin': 1, 'customer_comms': 1, 'finance_ops': 1, 'github_actions': 2, 'security_ops': 1}`
- Actions with metadata notes: `3`
- Pilot fit: `strong`
- Fit reason: The intake includes multiple side-effecting actions where SMERC creates reviewable restraint or escalation decisions.

## Highest Exposure Actions

| Action | Posture | Irreversible Exposure | Reversible Capacity |
| --- | --- | ---: | ---: |
| `EXAMPLECO_SUPPORT_EMAIL_BLAST` | `DENY` | 0.82 | 0.265 |
| `EXAMPLECO_CUSTOMER_REFUND_BATCH` | `THROTTLE` | 0.771 | 0.421 |
| `EXAMPLECO_CLOUD_IAM_POLICY_CHANGE` | `THROTTLE` | 0.745 | 0.454 |
| `EXAMPLECO_DISABLE_SUSPECTED_COMPROMISED_ACCOUNT` | `THROTTLE` | 0.489 | 0.739 |
| `EXAMPLECO_PROD_CANARY_DEPLOY` | `THROTTLE` | 0.454 | 0.668 |

## Action Decisions

### EXAMPLECO_PR_TEST_RUN

- Description: AI coding agent runs tests and static analysis for a pull request.
- Tool: `github_actions.test`
- Posture: `ALLOW`
- Enforcement state: `release`
- Scores: `{'irreversible_exposure_score': 0.069, 'reversible_capacity_score': 0.928, 'confidence_score': 0.921, 'operational_stress_score': 0.092, 'risk_adjusted_authorization_score': 0.927, 'cancel_reliability_score': 0.91}`
- Reason codes: `['RECOVERABILITY_ACCEPTABLE']`
- Controls: `['execute', 'record_replay', 'retain_cancel_handle']`
- Summary: Action 'EXAMPLECO_PR_TEST_RUN' received ALLOW. Irreversible exposure is 0.069, reversible capacity is 0.928, and authorization score is 0.927. Controls: execute, record_replay, retain_cancel_handle.

### EXAMPLECO_PROD_CANARY_DEPLOY

- Description: AI deployment assistant proposes a production canary release after merging a pull request.
- Tool: `github_actions.deploy`
- Posture: `THROTTLE`
- Enforcement state: `constrain`
- Scores: `{'irreversible_exposure_score': 0.454, 'reversible_capacity_score': 0.668, 'confidence_score': 0.75, 'operational_stress_score': 0.395, 'risk_adjusted_authorization_score': 0.662, 'cancel_reliability_score': 0.72}`
- Reason codes: `['EXTERNAL_SIDE_EFFECT']`
- Controls: `['limit_scope', 'preview_before_execution', 'record_replay', 'rate_limit_external_side_effect']`
- Summary: Action 'EXAMPLECO_PROD_CANARY_DEPLOY' received THROTTLE. Irreversible exposure is 0.454, reversible capacity is 0.668, and authorization score is 0.662. Controls: limit_scope, preview_before_execution, record_replay, rate_limit_external_side_effect.

### EXAMPLECO_CLOUD_IAM_POLICY_CHANGE

- Description: AI cloud assistant proposes broadening an IAM role used by production automation.
- Tool: `cloud.iam`
- Posture: `THROTTLE`
- Enforcement state: `constrain`
- Scores: `{'irreversible_exposure_score': 0.745, 'reversible_capacity_score': 0.454, 'confidence_score': 0.59, 'operational_stress_score': 0.586, 'risk_adjusted_authorization_score': 0.445, 'cancel_reliability_score': 0.58}`
- Reason codes: `['IRREVERSIBLE_EXPOSURE_HIGH', 'CONTAINMENT_WEAK', 'IMPACT_SCOPE_WIDE', 'EXTERNAL_SIDE_EFFECT', 'SENSITIVE_DATA']`
- Controls: `['limit_scope', 'preview_before_execution', 'record_replay', 'require_rollback_plan', 'rate_limit_external_side_effect', 'checkpoint_before_execution']`
- Summary: Action 'EXAMPLECO_CLOUD_IAM_POLICY_CHANGE' received THROTTLE. Irreversible exposure is 0.745, reversible capacity is 0.454, and authorization score is 0.445. Controls: limit_scope, preview_before_execution, record_replay, require_rollback_plan, rate_limit_external_side_effect, checkpoint_before_execution.
- Metadata notes: `['external side effect has slow rollback; reviewer should confirm rollback path', 'sensitive-data action has incomplete evidence; reviewer should confirm evidence source']`

### EXAMPLECO_CUSTOMER_REFUND_BATCH

- Description: AI finance assistant proposes issuing a batch of customer refunds from a support queue.
- Tool: `finance.refunds`
- Posture: `THROTTLE`
- Enforcement state: `constrain`
- Scores: `{'irreversible_exposure_score': 0.771, 'reversible_capacity_score': 0.421, 'confidence_score': 0.62, 'operational_stress_score': 0.546, 'risk_adjusted_authorization_score': 0.415, 'cancel_reliability_score': 0.53}`
- Reason codes: `['IRREVERSIBLE_EXPOSURE_HIGH', 'EXTERNAL_SIDE_EFFECT', 'SENSITIVE_DATA']`
- Controls: `['limit_scope', 'preview_before_execution', 'record_replay', 'require_rollback_plan', 'rate_limit_external_side_effect', 'checkpoint_before_execution']`
- Summary: Action 'EXAMPLECO_CUSTOMER_REFUND_BATCH' received THROTTLE. Irreversible exposure is 0.771, reversible capacity is 0.421, and authorization score is 0.415. Controls: limit_scope, preview_before_execution, record_replay, require_rollback_plan, rate_limit_external_side_effect, checkpoint_before_execution.
- Metadata notes: `['external side effect has slow rollback; reviewer should confirm rollback path', 'sensitive-data action has incomplete evidence; reviewer should confirm evidence source']`

### EXAMPLECO_SUPPORT_EMAIL_BLAST

- Description: AI support assistant proposes emailing all customers affected by a suspected outage before confirmation.
- Tool: `customer_comms.email`
- Posture: `DENY`
- Enforcement state: `block`
- Scores: `{'irreversible_exposure_score': 0.82, 'reversible_capacity_score': 0.265, 'confidence_score': 0.453, 'operational_stress_score': 0.718, 'risk_adjusted_authorization_score': 0.3, 'cancel_reliability_score': 0.42}`
- Reason codes: `['IRREVERSIBLE_EXPOSURE_HIGH', 'RECOVERY_CAPACITY_LOW', 'ROLLBACK_LATENCY_HIGH', 'CANCEL_RELIABILITY_WEAK', 'CONTAINMENT_WEAK', 'EVIDENCE_VALIDITY_LOW', 'IMPACT_SCOPE_WIDE', 'EXTERNAL_SIDE_EFFECT']`
- Controls: `['block_execution', 'explain_denial', 'preserve_replay', 'require_new_request']`
- Summary: Action 'EXAMPLECO_SUPPORT_EMAIL_BLAST' received DENY. Irreversible exposure is 0.820, reversible capacity is 0.265, and authorization score is 0.300. Controls: block_execution, explain_denial, preserve_replay, require_new_request.
- Metadata notes: `['external side effect has slow rollback; reviewer should confirm rollback path']`

### EXAMPLECO_DISABLE_SUSPECTED_COMPROMISED_ACCOUNT

- Description: AI security assistant proposes disabling a privileged account after suspicious activity.
- Tool: `identity.disable_account`
- Posture: `THROTTLE`
- Enforcement state: `constrain`
- Scores: `{'irreversible_exposure_score': 0.489, 'reversible_capacity_score': 0.739, 'confidence_score': 0.629, 'operational_stress_score': 0.489, 'risk_adjusted_authorization_score': 0.649, 'cancel_reliability_score': 0.76}`
- Reason codes: `['IRREVERSIBLE_EXPOSURE_ELEVATED', 'ANOMALY_PRESSURE_HIGH', 'EXTERNAL_SIDE_EFFECT', 'SENSITIVE_DATA']`
- Controls: `['limit_scope', 'preview_before_execution', 'record_replay', 'rate_limit_external_side_effect']`
- Summary: Action 'EXAMPLECO_DISABLE_SUSPECTED_COMPROMISED_ACCOUNT' received THROTTLE. Irreversible exposure is 0.489, reversible capacity is 0.739, and authorization score is 0.649. Controls: limit_scope, preview_before_execution, record_replay, rate_limit_external_side_effect.

## Recommended Next Action

Use the highest-exposure actions in a review call, ask human reviewers to label the preferred posture, and proceed to observe-mode pilot only if reviewer labels and workflow ownership are available.
