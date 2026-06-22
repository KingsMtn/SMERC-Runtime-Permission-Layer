# SMERC-F Policy Calibration And Audit

## Purpose

SMERC-F separates the decision mechanism from institution-specific risk appetite. The repository includes three transparent reference profiles:

- `conservative`: earlier throttling, escalation, freezing, and denial
- `balanced`: default reference behavior
- `permissive`: later intervention for controlled comparison

These are calibration examples, not approved financial policies.

## SMERC Signal Mapping

| SMERC Dimension | SMERC-F Interpretation |
| --- | --- |
| Structural | authorization support, counterparty concentration, liquidity concentration |
| Momentum | agent velocity, accelerating market instability |
| Entropy | model disagreement, settlement anomalies, evidence deterioration |
| Range | exposure concentration, collateral stress, stablecoin imbalance |
| Confidence | evidence validity and agreement across decision inputs |

Reversibility is evaluated across all dimensions because an error that can be contained or reversed is operationally different from an irreversible capital movement.

## Policy Guarantees

For the same input, the reference policies are tested to preserve monotonic restraint:

```text
severity(conservative) >= severity(balanced) >= severity(permissive)
```

This does not prove that any policy is correct. It proves that calibration changes behavior in the intended direction.

## Deterministic Decision Hash

Every decision includes a SHA-256 `decision_hash` derived from:

- normalized action signals
- policy name and version
- state
- scores
- drivers
- controls

Timestamps and replay IDs are excluded, so identical inputs under the same policy produce the same decision hash.

## Tamper-Evident Audit Chain

The audit chain records:

- decision hash
- policy version
- state
- drivers
- controls
- prior record hash
- record hash

Override records additionally require:

- reviewer identity
- original state
- replacement state
- written rationale

Changing a prior record invalidates its hash and every downstream link.

## Commands

Compare policy outcomes:

```bash
python -m reference_engine.financial_policy_comparison \
  examples/financial_action_requests.json \
  --json-output reports/smerc_f_policy_comparison.json \
  --report reports/SMERC_F_Policy_Comparison.md
```

Generate an audit chain:

```bash
python -m reference_engine.financial_audit \
  examples/financial_action_requests.json \
  --policy balanced \
  --output reports/smerc_f_audit_sample.json
```

## Production Boundary

Tamper-evident hashes do not provide identity, non-repudiation, immutable storage, key management, or regulatory recordkeeping by themselves. Production deployment would require authenticated reviewers, protected signing keys, durable storage, retention rules, access controls, and independent security review.

