# SMERC Scoring Invariants Report

This report verifies declared score behavior for the recoverability and Model/Agent Fitness engines.

It does not prove production incident reduction, customer-calibrated thresholds, or financial-risk prediction.

- Total invariants: 10
- Passed: 10
- Failed: 0
- Status: PASS

## Results

### RECOVERY_REVERSIBILITY_MONOTONIC - PASS

- Engine: `recoverability`
- Description: Higher reversibility must not increase irreversible exposure and must not reduce reversible capacity or authorization score.
- Expectation: irreversible_exposure_score <= prior value; reversible_capacity_score >= prior value; risk_adjusted_authorization_score >= prior value
- Before: `{"irreversible_exposure_score": 0.458, "reversible_capacity_score": 0.528, "risk_adjusted_authorization_score": 0.561}`
- After: `{"irreversible_exposure_score": 0.372, "reversible_capacity_score": 0.636, "risk_adjusted_authorization_score": 0.632}`

### RECOVERY_ROLLBACK_LATENCY_MONOTONIC - PASS

- Engine: `recoverability`
- Description: Higher rollback latency must not reduce exposure or stress and must not increase recovery capacity or authorization score.
- Expectation: irreversible_exposure_score >= prior value; operational_stress_score >= prior value; reversible_capacity_score <= prior value; risk_adjusted_authorization_score <= prior value
- Before: `{"irreversible_exposure_score": 0.458, "operational_stress_score": 0.481, "reversible_capacity_score": 0.528, "risk_adjusted_authorization_score": 0.561}`
- After: `{"irreversible_exposure_score": 0.525, "operational_stress_score": 0.52, "reversible_capacity_score": 0.456, "risk_adjusted_authorization_score": 0.512}`

### RECOVERY_EVIDENCE_VALIDITY_MONOTONIC - PASS

- Engine: `recoverability`
- Description: Lower evidence validity must not increase confidence or authorization and must not reduce operational stress.
- Expectation: confidence_score <= prior value; risk_adjusted_authorization_score <= prior value; operational_stress_score >= prior value
- Before: `{"confidence_score": 0.627, "operational_stress_score": 0.481, "risk_adjusted_authorization_score": 0.561}`
- After: `{"confidence_score": 0.459, "operational_stress_score": 0.542, "risk_adjusted_authorization_score": 0.492}`

### RECOVERY_ANOMALY_PRESSURE_MONOTONIC - PASS

- Engine: `recoverability`
- Description: Higher anomaly pressure must not increase confidence and must not reduce operational stress.
- Expectation: confidence_score <= prior value; operational_stress_score >= prior value
- Before: `{"confidence_score": 0.627, "operational_stress_score": 0.481}`
- After: `{"confidence_score": 0.533, "operational_stress_score": 0.589}`

### RECOVERY_EXTERNAL_AND_SENSITIVE_RISK - PASS

- Engine: `recoverability`
- Description: External side effects and sensitive data must not reduce irreversible exposure.
- Expectation: irreversible_exposure_score >= prior value
- Before: `{"irreversible_exposure_score": 0.458}`
- After: `{"irreversible_exposure_score": 0.623}`

### FITNESS_DATA_BOUNDARY_FAIL_CLOSED - PASS

- Engine: `model_fitness`
- Description: A data-boundary violation must block an executor even when capability and reliability scores are strong.
- Expectation: candidate is blocked with DATA_BOUNDARY_EXCEEDED
- Before: `{"executor_id": "deployment_guardian"}`
- After: `{"blocked_executors": ["deployment_guardian"], "blocking_reasons": ["DATA_BOUNDARY_EXCEEDED"]}`

### FITNESS_TOOL_AUTHORITY_FAIL_CLOSED - PASS

- Engine: `model_fitness`
- Description: A tool-authority gap must block an executor even when general capability scores are strong.
- Expectation: candidate is blocked with INSUFFICIENT_TOOL_AUTHORITY
- Before: `{"executor_id": "deployment_guardian"}`
- After: `{"blocked_executors": ["deployment_guardian"], "blocking_reasons": ["INSUFFICIENT_TOOL_AUTHORITY"]}`

### FITNESS_CAPABILITY_GAP_FAIL_CLOSED - PASS

- Engine: `model_fitness`
- Description: A required-capability gap must block an executor despite low cost and latency.
- Expectation: candidate is blocked with REQUIRED_CAPABILITY_GAP
- Before: `{"executor_id": "deployment_guardian"}`
- After: `{"blocked_executors": ["deployment_guardian"], "blocking_reasons": ["REQUIRED_CAPABILITY_GAP"]}`

### FITNESS_RISK_PRESSURE_REDUCES_ADJUSTED_SCORE - PASS

- Engine: `model_fitness`
- Description: Higher task risk must not increase the risk-adjusted executor score for the same candidate set.
- Expectation: risk_pressure >= prior value; risk_adjusted_executor_score <= prior value
- Before: `{"risk_adjusted_executor_score": 0.702, "risk_pressure": 0.561}`
- After: `{"risk_adjusted_executor_score": 0.675, "risk_pressure": 0.652}`

### FITNESS_SAFETY_HISTORY_IMPROVES_FIT - PASS

- Engine: `model_fitness`
- Description: Higher safety history must not reduce reliability, recoverability, or model fitness for an otherwise identical qualified executor.
- Expectation: recoverability_fit >= prior value; reliability_fit >= prior value; model_fitness_score >= prior value
- Before: `{"model_fitness_score": 0.841, "recoverability_fit": 0.544, "reliability_fit": 0.645}`
- After: `{"model_fitness_score": 0.885, "recoverability_fit": 0.644, "reliability_fit": 0.82}`
