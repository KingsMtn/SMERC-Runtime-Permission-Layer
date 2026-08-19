# SMERC-F Financial Public-Data Replay Report

Generated at: `2026-08-19T02:16:53+00:00`
Policy: `balanced`

## Purpose

This report shows how SMERC-F can ingest public-data-shaped financial, stablecoin, blockchain, and incident records and convert them into recoverability-aware pre-execution action postures.

It is designed for Fortune 500 financial-services review. It is not customer validation, AML compliance, fraud detection, sanctions screening, custody, settlement, trading, payment execution, or production certification.

## Evidence Boundary

Public-data-shaped replay only. Source records are normalized examples derived from public dataset schemas, public incident categories, and public documentation. The replay does not reconstruct customer telemetry, prove prevention, detect AML violations, screen sanctions, move funds, or certify production financial controls.

## Summary

- Public source rows: `6`
- Replay scenarios: `30`
- State counts: `{'ALLOW': 4, 'THROTTLE': 5, 'FREEZE': 13, 'DENY': 8, 'ESCALATE': 0}`
- Decision delta count: `26`
- Decision delta rate: `0.867`
- Restraint count: `26`
- Restraint rate: `0.867`

## Source Types

| Source type | Scenario count |
| --- | ---: |
| `chainabuse_report` | 5 |
| `defillama_hack_incident` | 5 |
| `dune_stablecoin_transfer` | 10 |
| `elliptic_bitcoin_graph` | 5 |
| `ethereum_bigquery_transfer` | 5 |

## Delta Types

| Delta | Count |
| --- | ---: |
| `CONTROL_ALLOW_SMERC_RESTRAINT` | 11 |
| `CONTROL_AND_SMERC_ALIGNED` | 4 |
| `CONTROL_REVIEW_SMERC_RESTRAINT` | 15 |

## Highest Irreversible Exposure Records

| Action | Source | Current control | SMERC-F | Exposure | Capacity | Key drivers |
| --- | --- | --- | --- | ---: | ---: | --- |
| `DEFILLAMA_ORACLE_INCIDENT_005_ACCELERATED_AUTOMATION` | `defillama_hack_incident` | `ALLOW` | `DENY` | 0.949 | 0.278 | `LIQUIDITY_CONCENTRATION`, `SETTLEMENT_ANOMALY`, `COUNTERPARTY_CONCENTRATION`, `MARKET_INSTABILITY` |
| `DEFILLAMA_ORACLE_INCIDENT_005_MARKET_STRESS` | `defillama_hack_incident` | `ALLOW` | `DENY` | 0.939 | 0.278 | `LIQUIDITY_CONCENTRATION`, `COLLATERAL_STRESS`, `SETTLEMENT_ANOMALY`, `STABLECOIN_IMBALANCE` |
| `DEFILLAMA_ORACLE_INCIDENT_005_MISSING_EVIDENCE` | `defillama_hack_incident` | `ALLOW` | `DENY` | 0.935 | 0.225 | `SETTLEMENT_ANOMALY`, `COUNTERPARTY_CONCENTRATION`, `LIQUIDITY_CONCENTRATION`, `COLLATERAL_STRESS` |
| `DEFILLAMA_ORACLE_INCIDENT_005_BASE` | `defillama_hack_incident` | `ALLOW` | `DENY` | 0.885 | 0.325 | `SETTLEMENT_ANOMALY`, `COUNTERPARTY_CONCENTRATION`, `COLLATERAL_STRESS`, `STABLECOIN_IMBALANCE` |
| `DEFILLAMA_ORACLE_INCIDENT_005_REDUCED_SCOPE` | `defillama_hack_incident` | `ALLOW` | `DENY` | 0.885 | 0.325 | `SETTLEMENT_ANOMALY`, `COUNTERPARTY_CONCENTRATION`, `COLLATERAL_STRESS`, `STABLECOIN_IMBALANCE` |
| `CHAINABUSE_VERIFIED_004_MARKET_STRESS` | `chainabuse_report` | `ALERT` | `DENY` | 0.87 | 0.268 | `SETTLEMENT_ANOMALY`, `COUNTERPARTY_CONCENTRATION`, `LIQUIDITY_CONCENTRATION`, `STABLECOIN_IMBALANCE` |
| `ELLIPTIC_UNKNOWN_GRAPH_RISK_006_MARKET_STRESS` | `elliptic_bitcoin_graph` | `REVIEW` | `DENY` | 0.849 | 0.271 | `LIQUIDITY_CONCENTRATION`, `COUNTERPARTY_CONCENTRATION`, `SETTLEMENT_ANOMALY`, `STABLECOIN_IMBALANCE` |
| `CHAINABUSE_VERIFIED_004_ACCELERATED_AUTOMATION` | `chainabuse_report` | `ALERT` | `DENY` | 0.832 | 0.268 | `SETTLEMENT_ANOMALY`, `COUNTERPARTY_CONCENTRATION`, `AGENT_VELOCITY`, `LIQUIDITY_CONCENTRATION` |
| `ELLIPTIC_UNKNOWN_GRAPH_RISK_006_ACCELERATED_AUTOMATION` | `elliptic_bitcoin_graph` | `REVIEW` | `FREEZE` | 0.81 | 0.275 | `COUNTERPARTY_CONCENTRATION`, `SETTLEMENT_ANOMALY`, `LIQUIDITY_CONCENTRATION`, `AGENT_VELOCITY` |
| `CHAINABUSE_VERIFIED_004_MISSING_EVIDENCE` | `chainabuse_report` | `ALERT` | `FREEZE` | 0.805 | 0.23 | `SETTLEMENT_ANOMALY`, `COUNTERPARTY_CONCENTRATION`, `LIQUIDITY_CONCENTRATION`, `STABLECOIN_IMBALANCE` |

## Fortune 500 Review Interpretation

The useful question is not whether SMERC-F replaces financial-crime, blockchain-analytics, IAM, OPA, or approval systems. It does not. The useful question is whether those systems can provide risk or policy context while SMERC-F adds a recoverability-aware action posture before automation executes.

A financial reviewer should inspect scenarios where the current control outcome is `ALLOW` but SMERC-F returns `THROTTLE`, `FREEZE`, or `ESCALATE`. Those are the candidate cases where recoverability may add a governance signal.

## Public Data Sources Represented

- Dune stablecoin transfer and balance schema documentation
- Google BigQuery Ethereum public dataset documentation
- Chainabuse reported-address API documentation
- DefiLlama public hacks database categories
- Elliptic public Bitcoin transaction graph dataset description
