# SMERC-F Replay Validation

## Objective

Evaluate whether SMERC-F produces coherent, explainable state transitions as financial stress and recoverability assumptions change through time.

This is not a prediction study.

## Evidence Boundary

Each replay scenario contains two deliberately separated layers:

1. Historical context and authoritative source links.
2. Analyst-assigned SMERC-F signal values and hypothetical proposed actions.

The numerical values are not presented as measured institution telemetry, reconstructed internal decisions, or evidence that SMERC-F would have prevented an incident.

## Included Scenarios

- March 2020 Treasury and funding-market stress
- Silicon Valley Bank failure and regional-bank stress
- USDC reserve-access disruption

## Replay Outputs

- chronological SMERC-F state
- irreversible exposure
- reversible capacity
- primary drivers
- recommended controls
- state transitions
- peak state and phase
- state distribution
- restrictive-posture rate

## Run The Replay

```bash
python -m reference_engine.financial_replay \
  examples/financial_replay_scenarios.json \
  --json-output reports/smerc_f_replay_results.json \
  --report reports/SMERC_F_Replay_Report.md
```

## Appropriate Interpretation

A useful replay should demonstrate:

- deterministic outputs for identical inputs
- increasing restraint under assigned stress
- understandable reasons for state transitions
- lower restraint only when recovery assumptions improve
- no unsupported claim of prediction or prevention

## Evidence Still Required

- institution-provided telemetry
- reviewer labels from treasury and risk professionals
- comparison against existing approval behavior
- false release and false constraint measurement
- policy calibration
- latency measurement
- override and accountability testing
- legal, compliance, model-risk, and security review

