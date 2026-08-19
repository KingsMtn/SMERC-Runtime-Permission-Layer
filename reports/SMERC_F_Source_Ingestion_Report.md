# SMERC-F Source Ingestion Report

Generated at: `2026-08-19T02:07:55+00:00`
Policy: `balanced`

## Purpose

This report shows how exported financial, stablecoin, blockchain, and incident rows can be normalized into SMERC-F replay inputs before recoverability scoring.

It is an ingestion and replay proof, not customer validation, AML compliance, sanctions screening, fraud detection, custody, settlement, trading, payment execution, or production certification.

## Summary

- Source export rows: `6`
- Normalized SMERC-F rows: `6`
- Replay scenarios: `30`
- State counts: `{'ALLOW': 5, 'THROTTLE': 4, 'FREEZE': 13, 'DENY': 7, 'ESCALATE': 1}`
- Decision delta rate: `0.833`
- Restraint rate: `0.833`

## Source Export Formats

| Source export format | Rows |
| --- | ---: |
| `chainabuse_address_report` | 1 |
| `defillama_hack_incident` | 1 |
| `dune_stablecoin_transfer_export` | 2 |
| `elliptic_bitcoin_graph_row` | 1 |
| `ethereum_bigquery_token_transfer` | 1 |

## Normalized Source Types

| Normalized source type | Rows |
| --- | ---: |
| `chainabuse_report` | 5 |
| `defillama_hack_incident` | 5 |
| `dune_stablecoin_transfer` | 10 |
| `elliptic_bitcoin_graph` | 5 |
| `ethereum_bigquery_transfer` | 5 |

## Highest Exposure Records

| Action | Source | Current control | SMERC-F | Exposure | Capacity |
| --- | --- | --- | --- | ---: | ---: |
| `DEFILLAMA_ORACLE_INCIDENT_005_MARKET_STRESS` | `defillama_hack_incident` | `ALLOW` | `DENY` | 0.932 | 0.297 |
| `DEFILLAMA_ORACLE_INCIDENT_005_ACCELERATED_AUTOMATION` | `defillama_hack_incident` | `ALLOW` | `DENY` | 0.918 | 0.297 |
| `DEFILLAMA_ORACLE_INCIDENT_005_MISSING_EVIDENCE` | `defillama_hack_incident` | `ALLOW` | `DENY` | 0.906 | 0.244 |
| `DEFILLAMA_ORACLE_INCIDENT_005_BASE` | `defillama_hack_incident` | `ALLOW` | `DENY` | 0.846 | 0.344 |
| `DEFILLAMA_ORACLE_INCIDENT_005_REDUCED_SCOPE` | `defillama_hack_incident` | `ALLOW` | `DENY` | 0.846 | 0.344 |
| `CHAINABUSE_VERIFIED_004_MARKET_STRESS` | `chainabuse_report` | `ALERT` | `DENY` | 0.845 | 0.282 |
| `ELLIPTIC_UNKNOWN_GRAPH_RISK_006_MARKET_STRESS` | `elliptic_bitcoin_graph` | `REVIEW` | `DENY` | 0.824 | 0.285 |
| `CHAINABUSE_VERIFIED_004_ACCELERATED_AUTOMATION` | `chainabuse_report` | `ALERT` | `FREEZE` | 0.808 | 0.282 |

## Evidence Boundary

Source export ingestion only. The adapter accepts public-data-shaped exports and normalizes them into SMERC-F metadata rows. It does not call vendor APIs, enrich addresses, determine illicit activity, screen sanctions, move funds, or certify financial controls.

## Financial-Services Interpretation

The useful review question is whether exported metadata from existing systems can feed a recoverability checkpoint before automated financial actions execute. Existing AML, fraud, blockchain analytics, identity, policy, and approval systems remain the source systems. SMERC-F adds a pre-execution recoverability posture and replay evidence.
