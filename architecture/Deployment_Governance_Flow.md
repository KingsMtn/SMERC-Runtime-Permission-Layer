# Deployment Governance Flow

## Shadow Mode

Run SMERC beside existing workflows without enforcing decisions. Compare SMERC outcomes against human decisions, incident history, false positives, false negatives, and operational tolerance.

## Advisory Mode

Display SMERC outputs to reviewers and operators while existing controls remain authoritative. Measure decision usefulness and calibrate thresholds.

## Enforcement Mode

Authorize the enforcement layer to apply `ALLOW`, `THROTTLE`, `DENY`, `FREEZE`, and `ESCALATE` under approved policy profiles. Eligible `ALLOW` and `THROTTLE` decisions may issue short-lived action-bound permits; executors verify and consume them once before acting.

## Review Requirements

- `THROTTLE`: review when repeated, high value, safety relevant, or customer impacting.
- `DENY`: preserve record and route by policy.
- `FREEZE`: alert accountable owner and require explicit release.

## Governance Metrics

- Action volume by decision.
- Freeze rate by domain.
- Override rate and override outcomes.
- Incident rate after `ALLOW`.
- Review latency.
- False constraint and missed-risk analysis.
- Permit issuance, expiry, rejection, replay, and consumption latency.
