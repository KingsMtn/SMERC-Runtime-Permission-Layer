# SMERC-F Financial Source Ingestion

## Purpose

The SMERC-F Financial Source Ingestion Adapter turns exported financial, stablecoin, blockchain, and incident metadata into normalized SMERC-F replay rows.

The purpose is practical and narrow:

> Show Fortune 500 financial-services reviewers how source-system exports could feed recoverability-aware pre-execution scoring without touching live funds, customer records, wallet keys, or production execution.

This is not AML compliance, fraud detection, sanctions screening, custody, settlement, trading, payment execution, address attribution, vendor enrichment, or production certification.

## Supported Public-Data-Shaped Export Formats

The first adapter supports five source-export shapes:

- `dune_stablecoin_transfer_export`
- `ethereum_bigquery_token_transfer`
- `chainabuse_address_report`
- `defillama_hack_incident`
- `elliptic_bitcoin_graph_row`

These formats are based on public documentation and public dataset categories. The repository uses representative exported metadata, not proprietary vendor data or private customer telemetry.

## What It Produces

For each source export row, the adapter creates a normalized SMERC-F row with:

- source identity
- source type
- source URL
- chain
- asset
- proposed action
- actor type
- current control outcome
- evidence quality
- settlement finality
- recipient reputation
- liquidity concentration
- counterparty concentration
- market stress
- anomaly pressure
- automation velocity

Those normalized rows are then passed into the existing SMERC-F public-data replay harness.

## Run

```bash
python -m reference_engine.smerc_f_source_ingestion \
  examples/smerc_f_source_exports.json \
  --pretty
```

Outputs:

```text
examples/smerc_f_normalized_source_rows.json
reports/SMERC_F_Source_Ingestion_Report.md
reports/smerc_f_source_ingestion_report.json
reports/SMERC_F_Source_Ingestion_Replay_Report.md
reports/smerc_f_source_ingestion_replay_report.json
```

## Why This Matters

Financial institutions already operate many systems that can produce useful metadata:

- IAM and entitlement systems
- transaction-monitoring systems
- blockchain analytics tools
- fraud engines
- treasury systems
- deployment pipelines
- approval workflows
- incident-management systems

SMERC-F should not replace those systems. It should consume their exported metadata and add a recoverability-aware runtime posture before automation executes.

The review question is:

> Can exported metadata from existing financial systems reveal when an otherwise allowed or reviewed action should be constrained, frozen, denied, or escalated because recovery options are weak?

## Evidence Boundary

This adapter demonstrates ingestion shape, validation, normalization, replay, and reporting.

It does not:

- call live vendor APIs
- enrich blockchain addresses
- infer beneficial ownership
- classify illicit activity
- satisfy AML or sanctions obligations
- handle customer records
- move funds
- execute trades
- replace approval systems
- certify financial controls
- prove incident prevention

## Design-Partner Path

The safest path for a financial-services design partner is:

```text
existing source export -> metadata-only sample -> SMERC-F normalization -> shadow-mode replay -> reviewer labels -> evidence report
```

The first useful customer proof is not a production integration. It is a bounded comparison between existing control outcomes, SMERC-F posture, and reviewer judgment on exported metadata.
