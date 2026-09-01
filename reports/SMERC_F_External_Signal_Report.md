# SMERC-F External Financial Signal Adapter Report

Generated at: `2026-09-01T00:41:00+00:00`
Policy: `balanced`

## Purpose

This report shows how SMERC-F can consume external financial-risk and compliance-style signals as evidence before automated financial actions execute.

The point is not to replace AML, KYT, wallet screening, fraud, Travel Rule, custody, settlement, or compliance systems. The point is to use their outputs as evidence while SMERC-F adds recoverability-aware pre-execution posture.

## Summary

- Input actions: `6`
- Taxonomy action types: `13`
- State counts: `{'ALLOW': 2, 'THROTTLE': 0, 'FREEZE': 2, 'DENY': 0, 'ESCALATE': 2}`
- Authorized actions restrained by SMERC-F: `2`
- Authorized restraint rate: `0.333`

## Supported External Signal Providers

- `blockchain_analytics`
- `fraud_engine`
- `smart_contract_risk`
- `stablecoin_reserve_monitor`
- `transaction_monitoring`
- `travel_rule`
- `treasury_risk`
- `wallet_screening`

## Financial Action Taxonomy

| Action type | Count in sample |
| --- | ---: |
| `customer_refund_batch` | 0 |
| `payment_release` | 1 |
| `payment_retry` | 0 |
| `reserve_status_publish` | 0 |
| `smart_contract_admin_change` | 1 |
| `stablecoin_bridge_transfer` | 1 |
| `stablecoin_burn` | 0 |
| `stablecoin_mint` | 0 |
| `stablecoin_redemption` | 1 |
| `tokenized_collateral_move` | 0 |
| `transaction_limit_change` | 0 |
| `treasury_rebalance` | 1 |
| `wallet_permission_update` | 1 |

## Provider Counts

| Provider | Actions |
| --- | ---: |
| `blockchain_analytics` | 1 |
| `fraud_engine` | 2 |
| `smart_contract_risk` | 2 |
| `stablecoin_reserve_monitor` | 2 |
| `transaction_monitoring` | 2 |
| `travel_rule` | 1 |
| `treasury_risk` | 1 |
| `wallet_screening` | 2 |

## Highest Exposure Records

| Action | Existing control | SMERC-F | Exposure | Capacity | Providers | Drivers |
| --- | --- | --- | ---: | ---: | --- | --- |
| `SMERCF_EXT_BRIDGE_TRANSFER_004` | `ALLOW` | `FREEZE` | 0.718 | 0.308 | `blockchain_analytics`, `smart_contract_risk`, `transaction_monitoring` | `AGENT_VELOCITY`, `COUNTERPARTY_CONCENTRATION`, `SETTLEMENT_ANOMALY`, `LIQUIDITY_CONCENTRATION` |
| `SMERCF_EXT_STABLECOIN_REDEMPTION_001` | `ALLOW` | `FREEZE` | 0.694 | 0.337 | `stablecoin_reserve_monitor`, `transaction_monitoring` | `STABLECOIN_IMBALANCE`, `LIQUIDITY_CONCENTRATION`, `SETTLEMENT_ANOMALY`, `AGENT_VELOCITY` |
| `SMERCF_EXT_SMART_CONTRACT_ADMIN_005` | `ALERT` | `ESCALATE` | 0.636 | 0.245 | `smart_contract_risk`, `stablecoin_reserve_monitor` | `COLLATERAL_STRESS`, `SETTLEMENT_ANOMALY`, `LIQUIDITY_CONCENTRATION`, `AUTHORIZATION_SUPPORT_WEAK` |
| `SMERCF_EXT_PAYMENT_RELEASE_006` | `REVIEW` | `ALLOW` | 0.479 | 0.362 | `travel_rule`, `wallet_screening` | `LOW_REVERSIBILITY` |
| `SMERCF_EXT_WALLET_POLICY_002` | `REVIEW` | `ESCALATE` | 0.389 | 0.459 | `fraud_engine`, `wallet_screening` | `COUNTERPARTY_CONCENTRATION`, `AUTHORIZATION_SUPPORT_WEAK`, `LOW_REVERSIBILITY` |
| `SMERCF_EXT_ROUTINE_TREASURY_003` | `ALLOW` | `ALLOW` | 0.236 | 0.687 | `fraud_engine`, `treasury_risk` | `LOW_STRESS_REPLAYABLE_ACTION` |

## Work / Result / Impact

| Work | Result | Impact |
| --- | --- | --- |
| Normalize `stablecoin_bridge_transfer` with external signals from blockchain_analytics, smart_contract_risk, transaction_monitoring into SMERC-F recoverability fields. | Existing control was `ALLOW`; SMERC-F returned `FREEZE` with exposure 0.718 and capacity 0.308. | This is the target proof: existing systems allowed the action, but recoverability evidence supports restraint before execution. |
| Normalize `stablecoin_redemption` with external signals from stablecoin_reserve_monitor, transaction_monitoring into SMERC-F recoverability fields. | Existing control was `ALLOW`; SMERC-F returned `FREEZE` with exposure 0.694 and capacity 0.337. | This is the target proof: existing systems allowed the action, but recoverability evidence supports restraint before execution. |
| Normalize `smart_contract_admin_change` with external signals from smart_contract_risk, stablecoin_reserve_monitor into SMERC-F recoverability fields. | Existing control was `ALERT`; SMERC-F returned `ESCALATE` with exposure 0.636 and capacity 0.245. | SMERC-F converts review or alert evidence into a concrete pre-execution route and retained decision proof. |
| Normalize `payment_release` with external signals from travel_rule, wallet_screening into SMERC-F recoverability fields. | Existing control was `REVIEW`; SMERC-F returned `ALLOW` with exposure 0.479 and capacity 0.362. | SMERC-F preserves evidence while allowing a bounded action to proceed. |
| Normalize `wallet_permission_update` with external signals from fraud_engine, wallet_screening into SMERC-F recoverability fields. | Existing control was `REVIEW`; SMERC-F returned `ESCALATE` with exposure 0.389 and capacity 0.459. | SMERC-F converts review or alert evidence into a concrete pre-execution route and retained decision proof. |

## Evidence Boundary

External signal adapter only. SMERC-F consumes vendor-style AML/KYT, wallet, travel-rule, fraud, treasury, reserve, and smart-contract risk outputs as pre-execution evidence. It does not perform AML compliance, sanctions screening, address attribution, Travel Rule compliance, custody, settlement, transaction execution, legal determination, or production certification.
