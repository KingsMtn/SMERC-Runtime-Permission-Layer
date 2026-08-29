# SMERC-F Financial Public-Data Replay Report

Generated at: `2026-08-29T23:59:39+00:00`
Policy: `balanced`

## Purpose

This report shows how SMERC-F can ingest public-data-shaped financial, stablecoin, blockchain, and incident records and convert them into recoverability-aware pre-execution action postures.

It is designed for Fortune 500 financial-services review. It is not customer validation, AML compliance, fraud detection, sanctions screening, custody, settlement, trading, payment execution, or production certification.

## Evidence Boundary

Public-data-shaped replay only. Source records are normalized examples derived from public dataset schemas, public incident categories, and public documentation. The replay does not reconstruct customer telemetry, prove prevention, detect AML violations, screen sanctions, move funds, or certify production financial controls.

## Summary

- Public source rows: `10`
- Replay scenarios: `50`
- State counts: `{'ALLOW': 7, 'THROTTLE': 11, 'FREEZE': 16, 'DENY': 7, 'ESCALATE': 9}`
- Decision delta count: `43`
- Decision delta rate: `0.86`
- Restraint count: `43`
- Restraint rate: `0.86`

## Source Types

| Source type | Scenario count |
| --- | ---: |
| `chainabuse_report` | 10 |
| `defillama_hack_incident` | 15 |
| `dune_stablecoin_transfer` | 15 |
| `elliptic_bitcoin_graph` | 5 |
| `ethereum_bigquery_transfer` | 5 |

## Delta Types

| Delta | Count |
| --- | ---: |
| `CONTROL_ALLOW_SMERC_RESTRAINT` | 23 |
| `CONTROL_AND_SMERC_ALIGNED` | 7 |
| `CONTROL_REVIEW_SMERC_RESTRAINT` | 20 |

## Financial Reason Code Library

| Reason code | Count | Meaning |
| --- | ---: | --- |
| `AUTOMATION_VELOCITY_HIGH` | 15 | Automation speed is high enough that a bad action could compound before review. |
| `COUNTERPARTY_CONCENTRATION_HIGH` | 22 | Counterparty or recipient concentration creates a larger correlated exposure. |
| `FINANCIAL_EVIDENCE_WEAK` | 11 | The evidence available before execution is too thin for an automated financial action. |
| `GOVERNANCE_CHANGE_AUTHORITY_RISK` | 5 | A governance or authority-changing action may alter who can act later. |
| `LIQUIDITY_ROUTE_FRAGILE` | 16 | Liquidity and market stress suggest the action may not unwind cleanly. |
| `MARKET_STRESS_ELEVATED` | 12 | Market stress is high enough to make ordinary routing assumptions less reliable. |
| `NO_FINANCIAL_REASON_CODE_TRIGGERED` | 6 | No financial reason code triggered. |
| `REDEMPTION_PRESSURE_HIGH` | 11 | Stablecoin or reserve movement pressure suggests execution should slow or pause. |
| `REPORTED_ADDRESS_RISK` | 5 | A reported-address or incident signal should be preserved before action. |
| `SETTLEMENT_REVERSIBILITY_LOW` | 39 | Settlement finality or low reversibility limits recovery after execution. |
| `TOKENIZED_COLLATERAL_EXPOSURE_HIGH` | 7 | Collateral or tokenized-asset pressure raises the cost of acting too quickly. |

## Current Control Vs SMERC-F

| Current control | SMERC-F posture | Delta | Example impact |
| --- | --- | --- | --- |
| `ALLOW` | `THROTTLE` | `CONTROL_ALLOW_SMERC_RESTRAINT` | Candidate proof point: recoverability would add restraint before an action an existing control shape allowed. |
| `ALLOW` | `THROTTLE` | `CONTROL_ALLOW_SMERC_RESTRAINT` | Candidate proof point: recoverability would add restraint before an action an existing control shape allowed. |
| `ALLOW` | `FREEZE` | `CONTROL_ALLOW_SMERC_RESTRAINT` | Candidate proof point: recoverability would add restraint before an action an existing control shape allowed. |
| `ALLOW` | `FREEZE` | `CONTROL_ALLOW_SMERC_RESTRAINT` | Candidate proof point: recoverability would add restraint before an action an existing control shape allowed. |
| `ALLOW` | `FREEZE` | `CONTROL_ALLOW_SMERC_RESTRAINT` | Candidate proof point: recoverability would add restraint before an action an existing control shape allowed. |
| `ALLOW` | `ALLOW` | `CONTROL_AND_SMERC_ALIGNED` | Alignment case: SMERC-F preserved replay evidence without changing the current control direction. |
| `ALLOW` | `ALLOW` | `CONTROL_AND_SMERC_ALIGNED` | Alignment case: SMERC-F preserved replay evidence without changing the current control direction. |
| `ALLOW` | `ALLOW` | `CONTROL_AND_SMERC_ALIGNED` | Alignment case: SMERC-F preserved replay evidence without changing the current control direction. |
| `ALLOW` | `ALLOW` | `CONTROL_AND_SMERC_ALIGNED` | Alignment case: SMERC-F preserved replay evidence without changing the current control direction. |
| `ALLOW` | `ALLOW` | `CONTROL_AND_SMERC_ALIGNED` | Alignment case: SMERC-F preserved replay evidence without changing the current control direction. |
| `ALLOW` | `FREEZE` | `CONTROL_ALLOW_SMERC_RESTRAINT` | Candidate proof point: recoverability would add restraint before an action an existing control shape allowed. |
| `ALLOW` | `FREEZE` | `CONTROL_ALLOW_SMERC_RESTRAINT` | Candidate proof point: recoverability would add restraint before an action an existing control shape allowed. |

## Highest Irreversible Exposure Records

| Action | Source | Current control | SMERC-F | Exposure | Capacity | Financial codes | Key drivers |
| --- | --- | --- | --- | ---: | ---: | --- | --- |
| `DEFILLAMA_ORACLE_MANIPULATION_INCIDENT_MARKET_STRESS` | `defillama_hack_incident` | `ALLOW` | `DENY` | 0.925 | 0.287 | `REDEMPTION_PRESSURE_HIGH`, `SETTLEMENT_REVERSIBILITY_LOW`, `COUNTERPARTY_CONCENTRATION_HIGH`, `LIQUIDITY_ROUTE_FRAGILE` | `LIQUIDITY_CONCENTRATION`, `MARKET_INSTABILITY`, `COLLATERAL_STRESS`, `STABLECOIN_IMBALANCE` |
| `DEFILLAMA_ORACLE_MANIPULATION_INCIDENT_ACCELERATED_AUTOMATION` | `defillama_hack_incident` | `ALLOW` | `DENY` | 0.915 | 0.287 | `REDEMPTION_PRESSURE_HIGH`, `SETTLEMENT_REVERSIBILITY_LOW`, `COUNTERPARTY_CONCENTRATION_HIGH`, `LIQUIDITY_ROUTE_FRAGILE` | `MARKET_INSTABILITY`, `AGENT_VELOCITY`, `SETTLEMENT_ANOMALY`, `STABLECOIN_IMBALANCE` |
| `DEFILLAMA_ORACLE_MANIPULATION_INCIDENT_MISSING_EVIDENCE` | `defillama_hack_incident` | `ALLOW` | `DENY` | 0.892 | 0.251 | `REDEMPTION_PRESSURE_HIGH`, `FINANCIAL_EVIDENCE_WEAK`, `SETTLEMENT_REVERSIBILITY_LOW`, `COUNTERPARTY_CONCENTRATION_HIGH` | `SETTLEMENT_ANOMALY`, `MARKET_INSTABILITY`, `COLLATERAL_STRESS`, `STABLECOIN_IMBALANCE` |
| `DUNE_STABLECOIN_ISSUER_REDEMPTION_IMBALANCE_MARKET_STRESS` | `dune_stablecoin_transfer` | `ALLOW` | `DENY` | 0.852 | 0.356 | `REDEMPTION_PRESSURE_HIGH`, `SETTLEMENT_REVERSIBILITY_LOW`, `COUNTERPARTY_CONCENTRATION_HIGH`, `LIQUIDITY_ROUTE_FRAGILE` | `LIQUIDITY_CONCENTRATION`, `MARKET_INSTABILITY`, `STABLECOIN_IMBALANCE`, `COUNTERPARTY_CONCENTRATION` |
| `DEFILLAMA_ORACLE_MANIPULATION_INCIDENT_BASE` | `defillama_hack_incident` | `ALLOW` | `DENY` | 0.829 | 0.351 | `REDEMPTION_PRESSURE_HIGH`, `SETTLEMENT_REVERSIBILITY_LOW`, `COUNTERPARTY_CONCENTRATION_HIGH`, `LIQUIDITY_ROUTE_FRAGILE` | `SETTLEMENT_ANOMALY`, `STABLECOIN_IMBALANCE`, `COLLATERAL_STRESS`, `MARKET_INSTABILITY` |
| `DEFILLAMA_ORACLE_MANIPULATION_INCIDENT_REDUCED_SCOPE` | `defillama_hack_incident` | `ALLOW` | `DENY` | 0.829 | 0.351 | `REDEMPTION_PRESSURE_HIGH`, `SETTLEMENT_REVERSIBILITY_LOW`, `COUNTERPARTY_CONCENTRATION_HIGH`, `LIQUIDITY_ROUTE_FRAGILE` | `SETTLEMENT_ANOMALY`, `STABLECOIN_IMBALANCE`, `COLLATERAL_STRESS`, `MARKET_INSTABILITY` |
| `DUNE_STABLECOIN_ISSUER_REDEMPTION_IMBALANCE_ACCELERATED_AUTOMATION` | `dune_stablecoin_transfer` | `ALLOW` | `DENY` | 0.821 | 0.36 | `REDEMPTION_PRESSURE_HIGH`, `SETTLEMENT_REVERSIBILITY_LOW`, `COUNTERPARTY_CONCENTRATION_HIGH`, `LIQUIDITY_ROUTE_FRAGILE` | `AGENT_VELOCITY`, `LIQUIDITY_CONCENTRATION`, `COUNTERPARTY_CONCENTRATION`, `STABLECOIN_IMBALANCE` |
| `DEFILLAMA_GOVERNANCE_PROPOSAL_INCIDENT_MARKET_STRESS` | `defillama_hack_incident` | `REVIEW` | `FREEZE` | 0.8 | 0.334 | `SETTLEMENT_REVERSIBILITY_LOW`, `COUNTERPARTY_CONCENTRATION_HIGH`, `LIQUIDITY_ROUTE_FRAGILE`, `TOKENIZED_COLLATERAL_EXPOSURE_HIGH` | `MARKET_INSTABILITY`, `SETTLEMENT_ANOMALY`, `COLLATERAL_STRESS`, `LIQUIDITY_CONCENTRATION` |
| `CHAINABUSE_VERIFIED_ADDRESS_REPORT_MARKET_STRESS` | `chainabuse_report` | `ALERT` | `FREEZE` | 0.781 | 0.294 | `SETTLEMENT_REVERSIBILITY_LOW`, `COUNTERPARTY_CONCENTRATION_HIGH`, `REPORTED_ADDRESS_RISK` | `SETTLEMENT_ANOMALY`, `COUNTERPARTY_CONCENTRATION`, `COLLATERAL_STRESS`, `MARKET_INSTABILITY` |
| `DUNE_STABLECOIN_ISSUER_REDEMPTION_IMBALANCE_MISSING_EVIDENCE` | `dune_stablecoin_transfer` | `ALLOW` | `FREEZE` | 0.78 | 0.351 | `REDEMPTION_PRESSURE_HIGH`, `SETTLEMENT_REVERSIBILITY_LOW`, `COUNTERPARTY_CONCENTRATION_HIGH`, `LIQUIDITY_ROUTE_FRAGILE` | `LIQUIDITY_CONCENTRATION`, `STABLECOIN_IMBALANCE`, `COUNTERPARTY_CONCENTRATION`, `SETTLEMENT_ANOMALY` |

## Work / Result / Impact Examples

| Work | Result | Impact |
| --- | --- | --- |
| Replay resume_protocol_liquidity_rebalance from defillama_hack_incident metadata and compare the current `ALLOW` control outcome with SMERC-F `DENY`. | SMERC-F returned `DENY` with irreversible exposure 0.925 and financial reason codes: REDEMPTION_PRESSURE_HIGH, SETTLEMENT_REVERSIBILITY_LOW, COUNTERPARTY_CONCENTRATION_HIGH, LIQUIDITY_ROUTE_FRAGILE, TOKENIZED_COLLATERAL_EXPOSURE_HIGH, AUTOMATION_VELOCITY_HIGH, MARKET_STRESS_ELEVATED. | Candidate proof point: recoverability would add restraint before an action an existing control shape allowed. |
| Replay resume_protocol_liquidity_rebalance from defillama_hack_incident metadata and compare the current `ALLOW` control outcome with SMERC-F `DENY`. | SMERC-F returned `DENY` with irreversible exposure 0.915 and financial reason codes: REDEMPTION_PRESSURE_HIGH, SETTLEMENT_REVERSIBILITY_LOW, COUNTERPARTY_CONCENTRATION_HIGH, LIQUIDITY_ROUTE_FRAGILE, TOKENIZED_COLLATERAL_EXPOSURE_HIGH, AUTOMATION_VELOCITY_HIGH, MARKET_STRESS_ELEVATED. | Candidate proof point: recoverability would add restraint before an action an existing control shape allowed. |
| Replay resume_protocol_liquidity_rebalance from defillama_hack_incident metadata and compare the current `ALLOW` control outcome with SMERC-F `DENY`. | SMERC-F returned `DENY` with irreversible exposure 0.892 and financial reason codes: REDEMPTION_PRESSURE_HIGH, FINANCIAL_EVIDENCE_WEAK, SETTLEMENT_REVERSIBILITY_LOW, COUNTERPARTY_CONCENTRATION_HIGH, LIQUIDITY_ROUTE_FRAGILE, TOKENIZED_COLLATERAL_EXPOSURE_HIGH, AUTOMATION_VELOCITY_HIGH, MARKET_STRESS_ELEVATED. | Candidate proof point: recoverability would add restraint before an action an existing control shape allowed. |
| Replay approve_stablecoin_redemption_batch from dune_stablecoin_transfer metadata and compare the current `ALLOW` control outcome with SMERC-F `DENY`. | SMERC-F returned `DENY` with irreversible exposure 0.852 and financial reason codes: REDEMPTION_PRESSURE_HIGH, SETTLEMENT_REVERSIBILITY_LOW, COUNTERPARTY_CONCENTRATION_HIGH, LIQUIDITY_ROUTE_FRAGILE, TOKENIZED_COLLATERAL_EXPOSURE_HIGH, AUTOMATION_VELOCITY_HIGH, MARKET_STRESS_ELEVATED. | Candidate proof point: recoverability would add restraint before an action an existing control shape allowed. |
| Replay resume_protocol_liquidity_rebalance from defillama_hack_incident metadata and compare the current `ALLOW` control outcome with SMERC-F `DENY`. | SMERC-F returned `DENY` with irreversible exposure 0.829 and financial reason codes: REDEMPTION_PRESSURE_HIGH, SETTLEMENT_REVERSIBILITY_LOW, COUNTERPARTY_CONCENTRATION_HIGH, LIQUIDITY_ROUTE_FRAGILE, TOKENIZED_COLLATERAL_EXPOSURE_HIGH, AUTOMATION_VELOCITY_HIGH, MARKET_STRESS_ELEVATED. | Candidate proof point: recoverability would add restraint before an action an existing control shape allowed. |

## Fortune 500 Review Interpretation

The useful question is not whether SMERC-F replaces financial-crime, blockchain-analytics, IAM, OPA, or approval systems. It does not. The useful question is whether those systems can provide risk or policy context while SMERC-F adds a recoverability-aware action posture before automation executes.

A financial reviewer should inspect scenarios where the current control outcome is `ALLOW` but SMERC-F returns `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE`. Those are the candidate cases where recoverability may add a governance signal.

## Public Data Sources Represented

- Dune stablecoin transfer and balance schema documentation
- Google BigQuery Ethereum public dataset documentation
- Chainabuse reported-address API documentation
- DefiLlama public hacks database categories
- Elliptic public Bitcoin transaction graph dataset description
