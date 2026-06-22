# SMERC-F Replay Validation Report

## Method

Historical event context is sourced. Numerical SMERC-F inputs are analyst-assigned replay signals, not measured historical telemetry. This report evaluates state-transition coherence and makes no prediction claim.

## Summary

- Scenarios: 3
- Policy: balanced 1.0.0
- Timeline events: 9
- Restrictive posture rate: 44.4%
- Average irreversible exposure: 0.437
- Average reversible capacity: 0.650
- State distribution: {"ALLOW": 5, "FREEZE": 3, "THROTTLE": 1}

## March 2020 Treasury and funding-market stress

Event date: 2020-03

Peak state: `FREEZE` during **Acute dash-for-cash stress**.

| Phase | State | Exposure | Capacity | Primary drivers |
| --- | --- | ---: | ---: | --- |
| Pre-stress baseline | `ALLOW` | 0.144 | 0.867 | LOW_STRESS_REPLAYABLE_ACTION |
| Acute dash-for-cash stress | `FREEZE` | 0.718 | 0.413 | MARKET_INSTABILITY, AGENT_VELOCITY, LIQUIDITY_CONCENTRATION |
| Stabilization | `ALLOW` | 0.323 | 0.739 | LOW_STRESS_REPLAYABLE_ACTION |

Sources:
- [Federal Reserve Financial Stability Report, November 2020](https://www.federalreserve.gov/publications/2020-november-financial-stability-report-purpose.htm)

Replay limitation: Historical context is based on the cited Federal Reserve report. All numerical SMERC-F signals are analyst-assigned scenario inputs and are not reconstructed market observations.

## Silicon Valley Bank failure and regional-bank stress

Event date: 2023-03

Peak state: `FREEZE` during **Rapid liquidity deterioration**.

| Phase | State | Exposure | Capacity | Primary drivers |
| --- | --- | ---: | ---: | --- |
| Concentration build-up | `THROTTLE` | 0.432 | 0.660 | COUNTERPARTY_CONCENTRATION, LIQUIDITY_CONCENTRATION |
| Rapid liquidity deterioration | `FREEZE` | 0.776 | 0.319 | LIQUIDITY_CONCENTRATION, AGENT_VELOCITY, COUNTERPARTY_CONCENTRATION |
| Post-failure containment | `ALLOW` | 0.337 | 0.774 | COUNTERPARTY_CONCENTRATION |

Sources:
- [Federal Reserve Review of the Supervision and Regulation of Silicon Valley Bank](https://www.federalreserve.gov/publications/review-of-the-federal-reserves-supervision-and-regulation-of-silicon-valley-bank.htm)

Replay limitation: The cited review supplies historical context. SMERC-F signal values and proposed actions are synthetic analyst assumptions and do not represent SVB systems or decisions.

## USDC reserve-access disruption

Event date: 2023-03

Peak state: `FREEZE` during **Reserve-access uncertainty**.

| Phase | State | Exposure | Capacity | Primary drivers |
| --- | --- | ---: | ---: | --- |
| Normal reserve operations | `ALLOW` | 0.156 | 0.875 | LOW_STRESS_REPLAYABLE_ACTION |
| Reserve-access uncertainty | `FREEZE` | 0.739 | 0.426 | STABLECOIN_IMBALANCE, AGENT_VELOCITY, COUNTERPARTY_CONCENTRATION |
| Operational normalization | `ALLOW` | 0.308 | 0.779 | LOW_STRESS_REPLAYABLE_ACTION |

Sources:
- [Circle update on USDC and Silicon Valley Bank](https://www.circle.com/blog/an-update-on-usdc-and-silicon-valley-bank)

Replay limitation: Circle's public update supplies event context. Numerical signals and proposed treasury actions are synthetic and are not Circle telemetry or reconstructed internal decisions.

## Interpretation

These outputs demonstrate deterministic state transitions under the supplied replay assumptions. They do not establish predictive accuracy, causal risk reduction, regulatory compliance, or production readiness. Real validation requires institution-specific telemetry and reviewer comparison in shadow mode.

# SMERC-F Replay Validation Report

## Method

Historical event context is sourced. Numerical SMERC-F inputs are analyst-assigned replay signals, not measured historical telemetry. This report evaluates state-transition coherence and makes no prediction claim.

## Summary

- Scenarios: 3
- Timeline events: 9
- Restrictive posture rate: 44.4%
- Average irreversible exposure: 0.437
- Average reversible capacity: 0.650
- State distribution: {"ALLOW": 5, "FREEZE": 3, "THROTTLE": 1}

## March 2020 Treasury and funding-market stress

Event date: 2020-03

Peak state: `FREEZE` during **Acute dash-for-cash stress**.

| Phase | State | Exposure | Capacity | Primary drivers |
| --- | --- | ---: | ---: | --- |
| Pre-stress baseline | `ALLOW` | 0.144 | 0.867 | LOW_STRESS_REPLAYABLE_ACTION |
| Acute dash-for-cash stress | `FREEZE` | 0.718 | 0.413 | MARKET_INSTABILITY, AGENT_VELOCITY, LIQUIDITY_CONCENTRATION |
| Stabilization | `ALLOW` | 0.323 | 0.739 | LOW_STRESS_REPLAYABLE_ACTION |

Sources:
- [Federal Reserve Financial Stability Report, November 2020](https://www.federalreserve.gov/publications/2020-november-financial-stability-report-purpose.htm)

Replay limitation: Historical context is based on the cited Federal Reserve report. All numerical SMERC-F signals are analyst-assigned scenario inputs and are not reconstructed market observations.

## Silicon Valley Bank failure and regional-bank stress

Event date: 2023-03

Peak state: `FREEZE` during **Rapid liquidity deterioration**.

| Phase | State | Exposure | Capacity | Primary drivers |
| --- | --- | ---: | ---: | --- |
| Concentration build-up | `THROTTLE` | 0.432 | 0.660 | COUNTERPARTY_CONCENTRATION, LIQUIDITY_CONCENTRATION |
| Rapid liquidity deterioration | `FREEZE` | 0.776 | 0.319 | LIQUIDITY_CONCENTRATION, AGENT_VELOCITY, COUNTERPARTY_CONCENTRATION |
| Post-failure containment | `ALLOW` | 0.337 | 0.774 | COUNTERPARTY_CONCENTRATION |

Sources:
- [Federal Reserve Review of the Supervision and Regulation of Silicon Valley Bank](https://www.federalreserve.gov/publications/review-of-the-federal-reserves-supervision-and-regulation-of-silicon-valley-bank.htm)

Replay limitation: The cited review supplies historical context. SMERC-F signal values and proposed actions are synthetic analyst assumptions and do not represent SVB systems or decisions.

## USDC reserve-access disruption

Event date: 2023-03

Peak state: `FREEZE` during **Reserve-access uncertainty**.

| Phase | State | Exposure | Capacity | Primary drivers |
| --- | --- | ---: | ---: | --- |
| Normal reserve operations | `ALLOW` | 0.156 | 0.875 | LOW_STRESS_REPLAYABLE_ACTION |
| Reserve-access uncertainty | `FREEZE` | 0.739 | 0.426 | STABLECOIN_IMBALANCE, AGENT_VELOCITY, COUNTERPARTY_CONCENTRATION |
| Operational normalization | `ALLOW` | 0.308 | 0.779 | LOW_STRESS_REPLAYABLE_ACTION |

Sources:
- [Circle update on USDC and Silicon Valley Bank](https://www.circle.com/blog/an-update-on-usdc-and-silicon-valley-bank)

Replay limitation: Circle's public update supplies event context. Numerical signals and proposed treasury actions are synthetic and are not Circle telemetry or reconstructed internal decisions.

## Interpretation

These outputs demonstrate deterministic state transitions under the supplied replay assumptions. They do not establish predictive accuracy, causal risk reduction, regulatory compliance, or production readiness. Real validation requires institution-specific telemetry and reviewer comparison in shadow mode.

