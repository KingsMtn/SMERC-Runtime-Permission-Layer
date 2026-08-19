# SMERC-F Financial Public-Data Replay

## Purpose

The SMERC-F Financial Public-Data Replay Harness shows how public-data-shaped blockchain, stablecoin, transaction-monitoring, and incident records can be converted into recoverability-aware financial action requests.

The goal is narrow:

> Demonstrate that SMERC-F can ingest financial-action metadata and return a pre-execution posture that may differ from ordinary allow, review, alert, or block outcomes.

This is not customer validation, AML compliance, fraud detection, sanctions screening, custody, settlement, trading, payment execution, or production certification.

## Public Data Shapes Represented

The harness uses normalized records shaped after public documentation and public datasets:

- Dune stablecoin transfer and balance schemas
- Google BigQuery Ethereum public dataset documentation
- Chainabuse reported-address API documentation
- DefiLlama public DeFi hacks database categories
- Elliptic public Bitcoin transaction graph dataset description

The repository does not commit proprietary vendor data, private customer data, wallet secrets, raw regulated transaction payloads, or production financial records.

## What The Harness Tests

For each public-data-shaped row, the harness creates several replay variants:

- base
- reduced scope
- missing evidence
- accelerated automation
- market stress

Each replay is converted into a SMERC-F action request with:

- authorization support
- evidence validity
- reversibility
- liquidity concentration
- collateral stress
- settlement anomaly
- stablecoin imbalance
- counterparty concentration
- market instability
- model disagreement
- agent velocity

SMERC-F then returns:

- `ALLOW`
- `THROTTLE`
- `FREEZE`
- `DENY`
- `ESCALATE`
- irreversible exposure
- reversible capacity
- confidence
- drivers
- controls
- decision hash

## Run

```bash
python -m reference_engine.smerc_f_public_data_replay \
  examples/smerc_f_public_data_replay_inputs.json \
  --pretty
```

Outputs:

```text
reports/SMERC_F_Public_Data_Replay_Report.md
reports/smerc_f_public_data_replay_report.json
```

## Why It Matters To Financial Institutions

Financial institutions already have strong systems for:

- identity and access control
- policy enforcement
- fraud detection
- AML and sanctions screening
- blockchain analytics
- case management
- audit and compliance workflows

SMERC-F does not replace those systems.

SMERC-F adds a different question:

> If this action is allowed, reviewed, or alerted by existing systems, is automated execution recoverable enough to proceed now?

The important replay records are usually those where a current control outcome is `ALLOW` but SMERC-F returns `THROTTLE`, `FREEZE`, or `ESCALATE`. Those are candidate examples where recoverability may add useful restraint before execution.

## Evidence Boundary

This harness is public-data-shaped replay, not a claim that SMERC-F would have prevented historical incidents.

It does not:

- reconstruct source-system state
- know what an institution knew at the time
- infer private wallet ownership
- provide address attribution
- classify illicit activity
- satisfy AML or sanctions obligations
- authorize live financial execution
- prove production risk reduction

Its value is showing the data contract, transformation logic, scoring output, and reviewable report shape a financial-services design partner could inspect before supplying their own metadata-only examples.

## Next Customer Step

For a Fortune 500 financial-services reviewer, the next step is:

```text
one workflow family -> metadata-only action examples -> SMERC-F shadow-mode scoring -> reviewer labels -> evidence report
```

Use `docs/SMERC_F_Fortune_500_Financial_Services_Review.md` and `pilot_package/Fortune_500_Financial_Services_Review_Checklist.md` before discussing any sensitive workflow details.
