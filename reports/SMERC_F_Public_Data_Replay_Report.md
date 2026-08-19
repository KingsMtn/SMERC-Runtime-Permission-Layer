# SMERC-F Financial Public-Data Replay Report

Generated at: `2026-08-19T01:56:31+00:00`
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

## Highest Irreversible Exposure Records

| Action | Source | Current control | SMERC-F | Exposure | Capacity | Key drivers |
| --- | --- | --- | --- | ---: | ---: | --- |
| `DEFILLAMA_ORACLE_MANIPULATION_INCIDENT_MARKET_STRESS` | `defillama_hack_incident` | `ALLOW` | `DENY` | 0.925 | 0.287 | `LIQUIDITY_CONCENTRATION`, `MARKET_INSTABILITY`, `COLLATERAL_STRESS`, `STABLECOIN_IMBALANCE` |
| `DEFILLAMA_ORACLE_MANIPULATION_INCIDENT_ACCELERATED_AUTOMATION` | `defillama_hack_incident` | `ALLOW` | `DENY` | 0.915 | 0.287 | `MARKET_INSTABILITY`, `AGENT_VELOCITY`, `SETTLEMENT_ANOMALY`, `STABLECOIN_IMBALANCE` |
| `DEFILLAMA_ORACLE_MANIPULATION_INCIDENT_MISSING_EVIDENCE` | `defillama_hack_incident` | `ALLOW` | `DENY` | 0.892 | 0.251 | `SETTLEMENT_ANOMALY`, `MARKET_INSTABILITY`, `COLLATERAL_STRESS`, `STABLECOIN_IMBALANCE` |
| `DUNE_STABLECOIN_ISSUER_REDEMPTION_IMBALANCE_MARKET_STRESS` | `dune_stablecoin_transfer` | `ALLOW` | `DENY` | 0.852 | 0.356 | `LIQUIDITY_CONCENTRATION`, `MARKET_INSTABILITY`, `STABLECOIN_IMBALANCE`, `COUNTERPARTY_CONCENTRATION` |
| `DEFILLAMA_ORACLE_MANIPULATION_INCIDENT_BASE` | `defillama_hack_incident` | `ALLOW` | `DENY` | 0.829 | 0.351 | `SETTLEMENT_ANOMALY`, `STABLECOIN_IMBALANCE`, `COLLATERAL_STRESS`, `MARKET_INSTABILITY` |
| `DEFILLAMA_ORACLE_MANIPULATION_INCIDENT_REDUCED_SCOPE` | `defillama_hack_incident` | `ALLOW` | `DENY` | 0.829 | 0.351 | `SETTLEMENT_ANOMALY`, `STABLECOIN_IMBALANCE`, `COLLATERAL_STRESS`, `MARKET_INSTABILITY` |
| `DUNE_STABLECOIN_ISSUER_REDEMPTION_IMBALANCE_ACCELERATED_AUTOMATION` | `dune_stablecoin_transfer` | `ALLOW` | `DENY` | 0.821 | 0.36 | `AGENT_VELOCITY`, `LIQUIDITY_CONCENTRATION`, `COUNTERPARTY_CONCENTRATION`, `STABLECOIN_IMBALANCE` |
| `DEFILLAMA_GOVERNANCE_PROPOSAL_INCIDENT_MARKET_STRESS` | `defillama_hack_incident` | `REVIEW` | `FREEZE` | 0.8 | 0.334 | `MARKET_INSTABILITY`, `SETTLEMENT_ANOMALY`, `COLLATERAL_STRESS`, `LIQUIDITY_CONCENTRATION` |
| `CHAINABUSE_VERIFIED_ADDRESS_REPORT_MARKET_STRESS` | `chainabuse_report` | `ALERT` | `FREEZE` | 0.781 | 0.294 | `SETTLEMENT_ANOMALY`, `COUNTERPARTY_CONCENTRATION`, `COLLATERAL_STRESS`, `MARKET_INSTABILITY` |
| `DUNE_STABLECOIN_ISSUER_REDEMPTION_IMBALANCE_MISSING_EVIDENCE` | `dune_stablecoin_transfer` | `ALLOW` | `FREEZE` | 0.78 | 0.351 | `LIQUIDITY_CONCENTRATION`, `STABLECOIN_IMBALANCE`, `COUNTERPARTY_CONCENTRATION`, `SETTLEMENT_ANOMALY` |

## Fortune 500 Review Interpretation

The useful question is not whether SMERC-F replaces financial-crime, blockchain-analytics, IAM, OPA, or approval systems. It does not. The useful question is whether those systems can provide risk or policy context while SMERC-F adds a recoverability-aware action posture before automation executes.

A financial reviewer should inspect scenarios where the current control outcome is `ALLOW` but SMERC-F returns `THROTTLE`, `FREEZE`, or `ESCALATE`. Those are the candidate cases where recoverability may add a governance signal.

## Public Data Sources Represented

- Dune stablecoin transfer and balance schema documentation
- Google BigQuery Ethereum public dataset documentation
- Chainabuse reported-address API documentation
- DefiLlama public hacks database categories
- Elliptic public Bitcoin transaction graph dataset description
