# SMERC-F Pilot Evidence Packet

Generated at: `2026-08-20T00:29:17+00:00`

## Executive Summary

SMERC-F is a metadata-only shadow-mode recoverability review layer for automated financial actions. It asks whether an action that may be authorized by existing systems is recoverable enough to proceed.

This packet connects source ingestion, regulatory-context overlay, public-data replay, and reviewer go/no-go criteria into one financial-services review path.

## What The Current Evidence Shows

- Source export rows: `6`
- Normalized SMERC-F rows: `6`
- Source-ingestion replay scenarios: `30`
- Source-ingestion restraint rate: `0.833`
- Regulatory context rows: `6`
- Regulatory-context state changes: `3` of `30`
- Baseline restraint rate: `0.833`
- Context-enriched restraint rate: `0.867`
- Public replay scenarios: `50`
- Public replay decision-delta rate: `0.86`

## Evidence Chain

| Step | Meaning | Artifact |
| --- | --- | --- |
| `source_export` | Public-data-shaped source exports represent the kind of metadata a financial workflow or vendor system could provide. | `examples/smerc_f_source_exports.json` |
| `normalization` | Source exports are converted into SMERC-F replay rows without private customer data, wallet keys, or live execution instructions. | `examples/smerc_f_normalized_source_rows.json` |
| `regulatory_context_overlay` | Legislation-inspired operational context can adjust recoverability posture without interpreting law or determining compliance. | `reports/SMERC_F_Regulatory_Context_Report.md` |
| `public_replay` | SMERC-F expands source rows into replay variants and returns ALLOW, THROTTLE, FREEZE, DENY, or ESCALATE with drivers and controls. | `reports/SMERC_F_Public_Data_Replay_Report.md` |
| `reviewer_decision` | A financial-services reviewer compares SMERC-F posture against current controls and human judgment before any enforcement discussion. | `pilot_package/Fortune_500_Financial_Services_Review_Checklist.md` |

## Most Useful Review Examples

| Action | Source | Current control | SMERC-F | Exposure | Capacity | Why it matters |
| --- | --- | --- | --- | ---: | ---: | --- |
| `CHAINABUSE_VERIFIED_004_ACCELERATED_AUTOMATION` | `regulatory_context_overlay` | `baseline` | `DENY` | 0.832 | - | Regulatory-context overlay changed posture from FREEZE to DENY. |
| `BIGQUERY_ERC20_BATCH_003_MISSING_EVIDENCE` | `regulatory_context_overlay` | `baseline` | `FREEZE` | 0.694 | - | Regulatory-context overlay changed posture from ESCALATE to FREEZE. |
| `DUNE_USDT_CEX_TRANSFER_002_MARKET_STRESS` | `regulatory_context_overlay` | `baseline` | `THROTTLE` | 0.527 | - | Regulatory-context overlay changed posture from ALLOW to THROTTLE. |
| `DEFILLAMA_ORACLE_MANIPULATION_INCIDENT_MARKET_STRESS` | `defillama_hack_incident` | `ALLOW` | `DENY` | 0.925 | 0.287 | High irreversible exposure with explicit drivers and controls. |
| `DEFILLAMA_ORACLE_MANIPULATION_INCIDENT_ACCELERATED_AUTOMATION` | `defillama_hack_incident` | `ALLOW` | `DENY` | 0.915 | 0.287 | High irreversible exposure with explicit drivers and controls. |
| `DEFILLAMA_ORACLE_MANIPULATION_INCIDENT_MISSING_EVIDENCE` | `defillama_hack_incident` | `ALLOW` | `DENY` | 0.892 | 0.251 | High irreversible exposure with explicit drivers and controls. |
| `DUNE_STABLECOIN_ISSUER_REDEMPTION_IMBALANCE_MARKET_STRESS` | `dune_stablecoin_transfer` | `ALLOW` | `DENY` | 0.852 | 0.356 | High irreversible exposure with explicit drivers and controls. |
| `DEFILLAMA_ORACLE_MANIPULATION_INCIDENT_BASE` | `defillama_hack_incident` | `ALLOW` | `DENY` | 0.829 | 0.351 | High irreversible exposure with explicit drivers and controls. |

## Pilot Go Conditions

- one automated financial workflow family is available for metadata-only review
- reviewers can label whether SMERC-F posture is useful
- metadata excludes customer identifiers, raw regulated payloads, wallet keys, secrets, and live execution instructions
- existing financial controls remain source-of-truth during shadow mode
- reviewers accept the boundary that SMERC-F is not AML, sanctions, fraud, custody, settlement, or payment execution

## Stop Conditions

- safe metadata cannot be provided
- reviewers cannot compare posture with human judgment
- recoverability does not change review behavior
- the prospect wants production enforcement immediately
- the prospect expects SMERC-F to replace compliance, AML, fraud, sanctions, custody, settlement, or payment systems

## Success Metrics

- reviewer agreement rate
- false release candidates
- false restraint candidates
- useful THROTTLE decisions
- useful FREEZE decisions
- useful ESCALATE decisions
- metadata gaps
- posture distribution
- median and p95 scoring latency
- reviewer time impact

## Reviewer Questions

- Would SMERC-F have changed how your team reviewed any of these actions?
- Which metadata fields would your systems already provide?
- Which posture changes look useful versus noisy?
- Which actions should never be constrained because delay creates more harm?
- Which actions require stronger recoverability controls before automation proceeds?
- What evidence would be required before moving from observe mode to recommend mode?

## Claim Boundaries

- This packet is not AML compliance.
- This packet is not legal compliance.
- This packet is not fraud detection.
- This packet is not sanctions screening.
- This packet is not custody software.
- This packet is not settlement infrastructure.
- This packet is not payment execution.
- This packet is not production certification.
- This packet does not prove customer demand, incident reduction, regulatory approval, or production safety.

## Recommended Next Action

Offer a 30-day metadata-only shadow-mode review for one financial workflow family, using reviewer labels to test whether recoverability posture changes review behavior.

## Evidence Boundary

Pilot evidence packet only. It combines existing public-data-shaped SMERC-F artifacts into a review package. It does not prove customer demand, production suitability, incident reduction, legal compliance, AML compliance, fraud detection, sanctions screening, custody, settlement, payment execution, or production certification.
