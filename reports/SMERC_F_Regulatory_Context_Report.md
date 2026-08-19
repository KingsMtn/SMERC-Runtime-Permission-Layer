# SMERC-F Regulatory Context Report

Generated at: `2026-08-19T02:16:53+00:00`
Policy: `balanced`

## Purpose

This report shows how legislation-inspired operational context can inform SMERC-F recoverability scoring without claiming legal compliance.

The overlay is designed for financial-services review of stablecoin, tokenized-finance, custody, treasury, and settlement-adjacent automation.

## Summary

- Source export rows: `6`
- Regulatory context rows: `6`
- Normalized rows: `6`
- Replay scenarios: `30`
- Baseline state counts: `{'ALLOW': 5, 'THROTTLE': 4, 'FREEZE': 13, 'DENY': 7, 'ESCALATE': 1}`
- Context-enriched state counts: `{'ALLOW': 4, 'THROTTLE': 5, 'FREEZE': 13, 'DENY': 8, 'ESCALATE': 0}`
- Baseline restraint rate: `0.833`
- Context-enriched restraint rate: `0.867`
- State change count: `3`
- State change rate: `0.1`

## Regulatory Context Tiers

| Tier | Rows |
| --- | ---: |
| `elevated` | 1 |
| `low` | 1 |
| `watch` | 4 |

## State Changes After Context Overlay

| Action | Baseline | Context-enriched | Exposure delta | Drivers |
| --- | --- | --- | ---: | --- |
| `CHAINABUSE_VERIFIED_004_ACCELERATED_AUTOMATION` | `FREEZE` | `DENY` | 0.024 | `SETTLEMENT_ANOMALY`, `COUNTERPARTY_CONCENTRATION`, `AGENT_VELOCITY`, `LIQUIDITY_CONCENTRATION` |
| `BIGQUERY_ERC20_BATCH_003_MISSING_EVIDENCE` | `ESCALATE` | `FREEZE` | 0.019 | `COUNTERPARTY_CONCENTRATION`, `AGENT_VELOCITY`, `SETTLEMENT_ANOMALY`, `LIQUIDITY_CONCENTRATION` |
| `DUNE_USDT_CEX_TRANSFER_002_MARKET_STRESS` | `ALLOW` | `THROTTLE` | 0.017 | `MARKET_INSTABILITY`, `LIQUIDITY_CONCENTRATION`, `LOW_REVERSIBILITY` |

## Evidence Boundary

Regulatory context overlay only. The profile uses legislation-inspired operational metadata as risk context. It does not interpret law, provide legal advice, determine compliance, screen AML or sanctions, classify illicit activity, or authorize financial execution.

## How To Use This

Use this profile to discuss whether regulatory-context metadata should make an automated financial action more cautious before execution. Do not use it as legal advice or as a substitute for compliance, legal, risk, AML, sanctions, custody, settlement, or payment-control systems.
