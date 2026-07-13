# Benchmark Decision-Time Ledgers

The benchmark ledger builder converts runtime benchmark records into SMERC Decision Lifecycle Ledger records.

The purpose is to make benchmark evidence replayable and auditable without pretending it is live customer evidence.

## What It Builds

For each runtime benchmark scenario, SMERC creates a hash-chained DLL with:

1. `REQUEST`
2. `EVIDENCE`
3. `EVALUATION`

The ledger intentionally does not create:

- `HUMAN_INTERACTION`
- `EXECUTION`
- `OUTCOME`
- `LEARNING_RECOMMENDATION`

Those records require real pilot data, reviewer labels, execution reports, and follow-up outcome review.

## Why This Matters

The benchmark suite shows where SMERC differs from allow/deny policy. The decision-time ledger bundle shows whether each benchmark decision can be preserved as structured evidence.

That helps a CISO or design partner inspect:

- what was requested
- what evidence was available
- what SMERC recommended
- why the benchmark is incomplete without pilot evidence
- which records are hash-chain verifiable

## Run It

```bash
python -m reference_engine.benchmark_ledger_builder \
  reports/runtime_governance_benchmark.json \
  --json-output reports/runtime_benchmark_dll_bundle.json \
  --markdown-output reports/Runtime_Benchmark_DLL_Bundle.md \
  --pretty
```

## Evidence Boundary

This is decision-time proxy evidence. It is useful for CISO review, product inspection, regression tests, and pilot planning.

It does not prove:

- production execution behavior
- customer outcome improvement
- incident reduction
- human reviewer agreement
- compliance readiness
- immutable regulatory recordkeeping

Production deployment would require durable storage, access control, retention policy, key management, privacy review, customer-specific schemas, and integration with existing audit systems.
