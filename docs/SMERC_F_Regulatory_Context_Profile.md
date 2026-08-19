# SMERC-F Regulatory Context Profile

## Purpose

The SMERC-F Regulatory Context Profile uses legislation-inspired operational metadata to inform recoverability-aware financial action scoring.

It is designed for review of stablecoin, tokenized-finance, custody, treasury, payment, settlement, and automated financial workflows.

It does not interpret law, provide legal advice, determine compliance, perform AML screening, perform sanctions screening, classify illicit activity, move funds, settle transactions, or certify financial controls.

## Why Add Regulatory Context

Digital-asset and stablecoin regulation increases the number of operational facts that matter before automation executes.

Examples include:

- permitted issuer status
- reserve sensitivity
- redemption pressure
- custody or safekeeping dependency
- lawful-order compliance capability
- jurisdiction complexity
- customer-impact radius
- disclosure gaps

SMERC-F treats those as context signals, not legal conclusions.

## How It Works

The profile starts with exported source metadata from `reference_engine.smerc_f_source_ingestion`.

It then applies a regulatory-context overlay:

```text
source export -> normalized SMERC-F row -> regulatory context overlay -> replay -> posture comparison
```

The overlay can reduce evidence quality and increase anomaly, market-stress, counterparty-concentration, or liquidity-concentration pressure when operational context makes recovery harder.

## Run

```bash
python -m reference_engine.smerc_f_regulatory_context --pretty
```

Outputs:

```text
examples/smerc_f_regulatory_enriched_rows.json
reports/SMERC_F_Regulatory_Context_Report.md
reports/smerc_f_regulatory_context_report.json
reports/SMERC_F_Regulatory_Context_Replay_Report.md
reports/smerc_f_regulatory_context_replay_report.json
```

## What Reviewers Should Look For

The most useful records are state changes between baseline replay and context-enriched replay.

For example:

- `ALLOW` becoming `THROTTLE`
- `THROTTLE` becoming `FREEZE`
- `FREEZE` becoming `DENY`
- any posture becoming `ESCALATE`

Those changes do not prove legal risk. They show that regulatory-context metadata may affect recoverability and review posture.

## Commercial Boundary

SMERC-F can be positioned as a runtime recoverability checkpoint that consumes metadata from existing financial controls.

It should not be positioned as:

- AML software
- sanctions screening
- fraud detection
- legal compliance automation
- custody software
- settlement infrastructure
- transaction execution infrastructure
- regulatory reporting software

## Design-Partner Question

The useful question for a financial-services reviewer is:

> Which regulatory-context facts should make an otherwise authorized automated financial action more constrained before execution?

That question can be tested safely in shadow mode with metadata-only exports and reviewer labels.
