# SMERC-F Profile Packet

Pre-execution permission governance for proposed autonomous-capital actions.

This packet is a financial-governance profile review artifact. It is not a banking product, not a cryptocurrency, not a trading product, not a token, and not a production-certified financial control.

## Summary

- Actions evaluated: `5`
- Policies: `conservative, balanced, permissive`
- High-restraint outcomes: `8`

## Signal Taxonomy

- `treasury`: `liquidity_concentration`, `collateral_stress`
- `settlement`: `settlement_anomaly`
- `stablecoin`: `stablecoin_imbalance`
- `counterparty`: `counterparty_concentration`
- `market`: `market_instability`
- `behavioral`: `model_disagreement`
- `agent`: `agent_velocity`
- `governance`: `authorization_support`, `evidence_validity`, `reversibility`

## State Distribution

| Policy | State | Count |
| --- | --- | --- |
| `conservative` | `ALLOW` | `1` |
| `conservative` | `DENY` | `2` |
| `conservative` | `FREEZE` | `1` |
| `conservative` | `THROTTLE` | `1` |
| `balanced` | `ALLOW` | `1` |
| `balanced` | `DENY` | `1` |
| `balanced` | `FREEZE` | `2` |
| `balanced` | `THROTTLE` | `1` |
| `permissive` | `ALLOW` | `2` |
| `permissive` | `DENY` | `1` |
| `permissive` | `FREEZE` | `1` |
| `permissive` | `THROTTLE` | `1` |

## Evaluations

| Policy | Action | State | Exposure | Capacity | Key drivers |
| --- | --- | --- | --- | --- | --- |
| `conservative` | `TREASURY_REBALANCE_ROUTINE` | `ALLOW` | `0.131` | `0.887` | `LOW_STRESS_REPLAYABLE_ACTION` |
| `conservative` | `STABLECOIN_DEPEG_REALLOCATION` | `DENY` | `0.787` | `0.392` | `STABLECOIN_IMBALANCE`, `AGENT_VELOCITY`, `MARKET_INSTABILITY`, `SETTLEMENT_ANOMALY` |
| `conservative` | `COUNTERPARTY_EXPOSURE_INCREASE` | `THROTTLE` | `0.38` | `0.729` | `COUNTERPARTY_CONCENTRATION`, `AGENT_VELOCITY` |
| `conservative` | `UNAUTHORIZED_RESERVE_TRANSFER` | `DENY` | `0.789` | `0.19` | `AGENT_VELOCITY`, `COUNTERPARTY_CONCENTRATION`, `SETTLEMENT_ANOMALY`, `LIQUIDITY_CONCENTRATION` |
| `conservative` | `MODEL_DISAGREEMENT_COLLATERAL_POST` | `FREEZE` | `0.538` | `0.582` | `MODEL_DISAGREEMENT`, `COLLATERAL_STRESS`, `MARKET_INSTABILITY`, `COUNTERPARTY_CONCENTRATION` |
| `balanced` | `TREASURY_REBALANCE_ROUTINE` | `ALLOW` | `0.131` | `0.887` | `LOW_STRESS_REPLAYABLE_ACTION` |
| `balanced` | `STABLECOIN_DEPEG_REALLOCATION` | `FREEZE` | `0.787` | `0.392` | `STABLECOIN_IMBALANCE`, `AGENT_VELOCITY`, `MARKET_INSTABILITY`, `SETTLEMENT_ANOMALY` |
| `balanced` | `COUNTERPARTY_EXPOSURE_INCREASE` | `THROTTLE` | `0.38` | `0.729` | `COUNTERPARTY_CONCENTRATION`, `AGENT_VELOCITY` |
| `balanced` | `UNAUTHORIZED_RESERVE_TRANSFER` | `DENY` | `0.789` | `0.19` | `AGENT_VELOCITY`, `COUNTERPARTY_CONCENTRATION`, `SETTLEMENT_ANOMALY`, `LIQUIDITY_CONCENTRATION` |
| `balanced` | `MODEL_DISAGREEMENT_COLLATERAL_POST` | `FREEZE` | `0.538` | `0.582` | `MODEL_DISAGREEMENT`, `COLLATERAL_STRESS`, `MARKET_INSTABILITY` |
| `permissive` | `TREASURY_REBALANCE_ROUTINE` | `ALLOW` | `0.131` | `0.887` | `LOW_STRESS_REPLAYABLE_ACTION` |
| `permissive` | `STABLECOIN_DEPEG_REALLOCATION` | `FREEZE` | `0.787` | `0.392` | `STABLECOIN_IMBALANCE`, `AGENT_VELOCITY`, `MARKET_INSTABILITY`, `SETTLEMENT_ANOMALY` |
| `permissive` | `COUNTERPARTY_EXPOSURE_INCREASE` | `ALLOW` | `0.38` | `0.729` | `COUNTERPARTY_CONCENTRATION` |
| `permissive` | `UNAUTHORIZED_RESERVE_TRANSFER` | `DENY` | `0.789` | `0.19` | `AGENT_VELOCITY`, `COUNTERPARTY_CONCENTRATION`, `SETTLEMENT_ANOMALY`, `LIQUIDITY_CONCENTRATION` |
| `permissive` | `MODEL_DISAGREEMENT_COLLATERAL_POST` | `THROTTLE` | `0.538` | `0.582` | `MODEL_DISAGREEMENT`, `COLLATERAL_STRESS`, `MARKET_INSTABILITY` |

## Recommended Pilot Scope

- Historical replay and synthetic scenario review before live workflow use.
- Shadow-mode scoring only for first financial workflow pilot.
- No automated money movement, custody action, settlement instruction, or production blocking without legal, compliance, security, and operational approval.

## Commercial Limits

- SMERC-F is not a bank, broker-dealer, exchange, custodian, token, stablecoin, cryptocurrency, trading system, or investment product.
- The current profile is a reference governance profile, not institution-calibrated financial risk infrastructure.
- The profile does not predict market prices, solvency, depegs, liquidity events, or settlement failures.
- Production use requires institution-specific calibration, model-risk review, security review, compliance review, legal review, and accountable human ownership.
