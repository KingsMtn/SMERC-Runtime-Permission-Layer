# Public Benchmark Ingestion Pack

## Purpose

The Public Benchmark Ingestion Pack shows how SMERC can map public agent-governance, MCP-security, action-boundary, consequence, cloud-admin, and financial runtime benchmark categories into the same customer-evaluation path used by company pilots.

It is meant to answer a practical reviewer question:

> Can SMERC ingest the kinds of action-risk problems public benchmarks are already exploring, then return recoverability-aware posture, SPARTa route, autonomy-budget impact, and Decision Lifecycle Ledger evidence?

## What It Does

The pack accepts representative public benchmark-shaped examples as metadata rows and produces:

- normalized `smerc.customer-evaluation.v1` actions
- SMERC posture counts
- SPARTa route counts
- baseline-versus-SMERC deltas
- valid Decision Lifecycle Ledger counts
- a customer-evaluation report
- a public benchmark ingestion report

Run it:

```bash
python -m reference_engine.public_benchmark_ingestion examples/public_benchmark_ingestion_examples.json --pretty
```

Generated outputs:

- `examples/public_benchmark_normalized_customer_eval_actions.json`
- `reports/Public_Benchmark_Ingestion_Report.md`
- `reports/public_benchmark_ingestion_report.json`
- `reports/public_benchmark_customer_evaluation/Customer_Evaluation_Report.md`
- `reports/public_benchmark_customer_evaluation/customer_evaluation_report.json`

## Public Patterns Represented

The checked-in examples cover representative rows inspired by public benchmark categories:

- AgentGovBench-style identity propagation and fail-mode governance
- Agent Action Boundary-style action drift and safe-baseline actions
- MCP tool-poisoning and benign MCP tool baselines
- agentic red-team trajectory drift
- consequence and external-state recovery problems
- cloud-admin infrastructure action problems
- financial runtime action problems

## Evidence Boundary

This is not an official benchmark score.

The checked-in rows are representative metadata examples. They are not copied private customer data, official upstream benchmark datasets, official benchmark runner outputs, secrets, credentials, source code, raw logs, raw transactions, or production events.

Before SMERC claims performance on a named benchmark, the upstream dataset must be license-compatible, the official or documented runner must be used where available, and the report must disclose exactly which rows, versions, prompts, policies, thresholds, and environment were used.

## Work / Result / Impact

Work: translate public governance benchmark shapes into SMERC metadata without importing sensitive data or overstating benchmark status.

Result: the same SMERC engine evaluates each action through hard gates, recoverability scoring, SPARTa routing, autonomy budgeting, and ledger evidence.

Impact: a technical reviewer can see how SMERC relates to the public test landscape and where it adds recoverability-before-execution judgment beyond simple allow, review, or block baselines.

## Why It Matters

Many adjacent tools focus on finding risk, scanning prompts, observing agents, sandboxing actions, or enforcing static authorization.

SMERC's testable difference is the pre-execution action question:

> If this authorized agent or automation acts right now, is the action recoverable, bounded, supported by trusted evidence, and routed through the right control path?

The public benchmark ingestion pack makes that difference visible against categories reviewers already recognize: MCP tool risk, action-boundary drift, identity propagation, external consequences, and cloud or financial side effects.

## Next Useful Step

The next stronger proof is to add a license-compatible upstream dataset fixture and a reproducible runner that records:

- upstream benchmark source and version
- row count and inclusion criteria
- SMERC policy version
- latency and overhead
- posture distribution
- false-positive and false-negative review labels where human labels exist
- failures, skipped rows, and unsupported fields

That would move this from adapter-ready proof toward benchmark evidence.
