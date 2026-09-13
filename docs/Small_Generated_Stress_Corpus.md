# Small Generated Stress Corpus

## Purpose

The small generated stress corpus gives SMERC a deterministic fallback dataset when no external reviewer has provided customer-owned metadata yet.

It is intentionally metadata-only and compact. It exercises AWS-style cloud actions, MCP/tool-call governance, CI/CD deployment, security remediation, financial velocity, data mutation, network boundary changes, incident-pressure actions, and approved-intent drift.

## Run

```bash
python -m reference_engine.small_stress_corpus --pretty
```

This writes:

- `examples/smerc_stress_corpus_small.json`
- `reports/small_generated_stress_corpus_report.json`
- `reports/Small_Generated_Stress_Corpus_Report.md`
- `reports/small_generated_stress_corpus_customer_evaluation/customer_evaluation_report.json`
- `reports/small_generated_stress_corpus_customer_evaluation/Customer_Evaluation_Report.md`

## What It Proves

- SMERC can evaluate a compact generated corpus through the same customer-evaluation path used for reviewer-owned metadata.
- The generated rows produce posture counts, SPARTa route states, Decision Lifecycle Ledger evidence, and highest-exposure actions.
- The corpus gives reviewers a runnable fallback while the project waits for 5 to 25 metadata-only actions from one real workflow.

## What It Does Not Prove

This corpus is not customer validation, production evidence, AWS endorsement, incident reduction proof, or an official benchmark score.

The next validation gate remains customer-owned metadata replacement.
