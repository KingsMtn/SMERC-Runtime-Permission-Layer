# SMERC GitHub Actions Pilot Package

Generated: `2026-08-16T03:03:00+00:00`

## What This Is

A self-contained shadow-mode package showing where SMERC sits in a GitHub Actions workflow before action execution.

## Result

- Action: `deploy-prod-canary`
- Constraint eligible: `True`
- Eligibility labels: `['constraint_eligible']`
- Raw engine posture: `THROTTLE`
- Effective posture: `THROTTLE`
- SPARTa route: `CONSTRAINED_EXECUTE`
- Route executable: `True`
- Timing status: `ready`
- DLL valid: `True`

## Runtime Flow

```text
SPARK evidence -> Action Language -> Constraint Eligibility -> SMERC decision -> SPARTa route -> DLL -> Timing Evidence
```

## Pilot Runbook

1. Select one GitHub Actions workflow with real side effects and existing review expectations.
2. Run SMERC in observe mode first; do not block production workflow execution.
3. Collect non-secret SPARK evidence from repository, workflow, policy, identity, and rollback context.
4. Evaluate constraint eligibility before recoverability scoring.
5. Compare raw SMERC posture, eligibility-adjusted posture, SPARTa route, and existing reviewer judgment.
6. Record timing, unavailable evaluations, reviewer agreement, false release candidates, false constraint candidates, and useful constraint examples.
7. Move to recommend or enforce only after reviewer agreement and latency evidence justify it.

## Metrics To Collect In A Real Pilot

- `minimum_sample_size_before_claims`: 25
- `reviewer_agreement_rate`: measured during pilot
- `false_release_rate`: measured during pilot
- `false_constraint_rate`: measured during pilot
- `useful_constraint_rate`: measured during pilot
- `median_decision_latency_ms`: measured during pilot
- `p95_decision_latency_ms`: measured during pilot
- `workflow_overhead_ms`: measured during pilot
- `unavailable_evaluation_rate`: measured during pilot

## Local Generation Latency

- SPARK intake: `0.371` ms
- Constraint eligibility: `0.165` ms
- SMERC decision: `0.411` ms
- SPARTa route: `0.323` ms
- DLL: `0.213` ms
- DLL Intelligence: `1.326` ms
- Timing report: `0.102` ms
- Total generation: `3.019` ms

## Evidence Boundary

- This package is a runnable pilot artifact generator, not production certification.
- The default examples are synthetic and metadata-only.
- A customer pilot must replace examples with customer-approved non-secret workflow evidence.
- SMERC must remain in observe mode until customer reviewer agreement, latency, and failure-mode evidence justify stronger operation.
