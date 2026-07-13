# SMERC-F Financial Action Governance Profile

## Status

SMERC-F is an exploratory domain profile of the SMERC runtime permission engine. It is not a cryptocurrency, token, trading system, investment product, banking platform, or production-certified financial control.

The profile exists to demonstrate how SMERC's action-boundary model can be adapted to proposed treasury, settlement, liquidity, collateral, custody, and tokenized-finance actions.

## Positioning

> SMERC-F is pre-execution permission infrastructure for proposed autonomous-capital actions.

It evaluates whether an automated financial action should:

- `ALLOW`: proceed with monitoring and a retained reversal path
- `THROTTLE`: reduce size or velocity and require dual approval
- `FREEZE`: pause automation pending secondary validation
- `DENY`: block automated progression
- `ESCALATE`: route a potentially legitimate action to an accountable reviewer

## Architecture

```text
financial telemetry and model signals
        |
        v
signal normalization
        |
        v
SMERC-F financial permission profile
        |
        v
ALLOW / THROTTLE / FREEZE / DENY / ESCALATE
        |
        v
existing treasury, settlement, custody or workflow controls
```

Signal capture and execution remain external integration responsibilities. SMERC-F does not replace ledgers, identity systems, payment rails, custody systems, risk platforms, or supervisory controls.

## Input Signals

All numeric signals use the interval `0.0` to `1.0`:

- authorization support
- evidence validity
- reversibility
- liquidity concentration
- collateral stress
- settlement anomaly
- stablecoin imbalance
- counterparty concentration
- market instability
- model disagreement
- agent velocity

## Outputs

- state
- confidence
- aggregate signal risk
- irreversible exposure
- reversible capacity
- ranked driver codes
- execution controls
- recommended action
- replay ID

## Example

```bash
python -m reference_engine.financial_permission_profile \
  examples/financial_action_requests.json --pretty
```

For a profile-level packet across multiple policies:

```bash
python -m reference_engine.smerc_f_profile_packet \
  examples/financial_action_requests.json \
  --policies conservative balanced permissive \
  --pretty
```

See `docs/SMERC_F_Profile_Packet.md` and `reports/SMERC_F_Profile_Packet.md`.

## Intended Validation

The profile should first be evaluated through historical replay and shadow-mode workflow simulation. The objective is not to claim prediction accuracy. It is to measure whether state transitions and controls remain coherent under changing financial stress and recoverability conditions.

Useful evaluation measures include:

- reviewer agreement
- override rate
- false release rate
- false constraint rate
- action-size reduction under `THROTTLE`
- time to accountable review under `FREEZE` or `ESCALATE`
- consistency across replayed scenarios

## Limitations

- Thresholds are reference defaults, not institution-specific policy.
- Example scenarios are synthetic.
- Financial telemetry quality is not independently verified by this profile.
- The model does not predict market prices or solvency.
- It does not execute, custody, settle, or transfer assets.
- Production use would require institution-specific calibration, model-risk review, security review, compliance review, legal counsel, and accountable human ownership.

## Relationship To The Core Product

The core SMERC product remains the general runtime permission layer, with GitHub Actions as its first pilot integration. SMERC-F demonstrates domain extensibility; it does not replace or dilute the first commercial wedge.

