# SMERC Decision Lifecycle Ledger Report

Decision ID: `dll_example_ai_deploy_001`
Tenant: `design-partner`
Record count: `7`
Head record hash: `f3e79040a33cae7ac2f40b2cf6b9c8a3e9a23b8db6f8d3bfafc4c93cdc5b1f07`
Valid chain: `yes`

## Summary

- override_count: `0`
- rollback_performed: `False`
- rollback_success: `None`
- judged_correct: `True`
- pending_learning_recommendations: `1`

## Lifecycle Events

### 1. REQUEST

- Actor: `coding_agent`
- Recorded at: `2026-07-12T12:00:00+00:00`
- Record hash: `916424d9b000a20ac83c7d4ee8ea3b869693243729e364d35b5519fc37128e3b`

```json
{
  "environment": "production",
  "initiated_by": "coding_agent",
  "requested_operation": "Deploy generated authentication middleware change to production.",
  "risk_profile": "github_actions_deployment"
}
```

### 2. EVIDENCE

- Actor: `smerc-api`
- Recorded at: `2026-07-12T12:00:03+00:00`
- Record hash: `ddcfd44d6eee8b56121ab0b307ded80362444baed725da5530ac78927d8e891f`

```json
{
  "available_evidence": [
    "pull_request_checks",
    "unit_tests",
    "review_metadata"
  ],
  "confidence_score": 0.62,
  "external_dependencies": [
    "github_actions",
    "deployment_adapter"
  ],
  "missing_evidence": [
    "security_review",
    "rollback_drill"
  ],
  "model_version": "agent-model-unknown",
  "policy_version": "smerc.policy.v1:github-actions-strict"
}
```

### 3. EVALUATION

- Actor: `smerc-engine`
- Recorded at: `2026-07-12T12:00:04+00:00`
- Record hash: `3c037fce501d22ba2b9b4f489a56a656abda6be0497880e18cccd1b76db8b531`

```json
{
  "authorization_recommendation": "THROTTLE",
  "entropy_indicators": [
    "missing_security_review",
    "auth_boundary_change"
  ],
  "reason_codes": [
    "EVIDENCE_INCOMPLETE",
    "RECOVERY_PATH_PARTIAL"
  ],
  "recommended_safeguards": [
    "limit_scope",
    "preview_before_execution",
    "require_rollback_plan"
  ],
  "recoverability_score": 0.48,
  "structural_state": "high-impact production change with incomplete review evidence"
}
```

### 4. HUMAN_INTERACTION

- Actor: `security-reviewer-7`
- Recorded at: `2026-07-12T12:03:20+00:00`
- Record hash: `f1276047ca949516532ebae06f39e640daac111a7d025ad5ad6231a83b78261a`

```json
{
  "final_recommendation": "THROTTLE",
  "interaction": "accepted",
  "original_recommendation": "THROTTLE",
  "rationale": "Proceed only as a canary with rollback plan and preserved replay.",
  "reviewer_id": "security-reviewer-7"
}
```

### 5. EXECUTION

- Actor: `deployment-adapter`
- Recorded at: `2026-07-12T12:08:10+00:00`
- Record hash: `21d2583f46e553638b6420289ec606b7bce441fe39d7e1262caa5223db416b49`

```json
{
  "duration_ms": 184000,
  "executed_operation": "Canary deploy to 10 percent of production traffic.",
  "execution_status": "succeeded",
  "rollback_performed": false,
  "rollback_success": null,
  "started_at": "2026-07-12T12:05:00+00:00"
}
```

### 6. OUTCOME

- Actor: `pilot-review-lead`
- Recorded at: `2026-07-13T12:00:00+00:00`
- Record hash: `3038e383bc7aef5cad3a37753c662a7e309444d35718731f1faae60b12a4c104`

```json
{
  "controls_sufficient": true,
  "cost_incurred": 0.0,
  "customer_impact": "none observed",
  "financial_impact": "none observed",
  "judged_correct": true,
  "security_impact": "none observed",
  "time_to_recover_minutes": 0.0,
  "unexpected_consequences": false
}
```

### 7. LEARNING_RECOMMENDATION

- Actor: `smerc-dll`
- Recorded at: `2026-07-13T12:05:00+00:00`
- Record hash: `f3e79040a33cae7ac2f40b2cf6b9c8a3e9a23b8db6f8d3bfafc4c93cdc5b1f07`

```json
{
  "activation_status": "requires_review",
  "actual_outcome": "Canary deployment succeeded without rollback or observed impact.",
  "confidence_calibration_changes": [
    "No automatic calibration change; collect more samples."
  ],
  "expected_outcome": "Canary deployment proceeds without material incident under constraints.",
  "human_override_effectiveness": "reviewer accepted constraint; no override occurred",
  "prediction_error": "low",
  "recommended_policy_updates": [
    "Keep auth-boundary production changes out of direct ALLOW."
  ],
  "suggested_rule_modifications": [
    "Require rollback drill evidence before considering ALLOW."
  ]
}
```

## Boundary

This report is a pilot-grade lifecycle record. It is not a production immutable ledger, regulatory recordkeeping system, or automatic policy-update mechanism. Learning recommendations require human review before activation.
