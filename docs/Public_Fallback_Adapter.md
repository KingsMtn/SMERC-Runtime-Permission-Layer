# Public Fallback Adapter

## Purpose

This adapter is the first build after the public evidence fallback plan.

It focuses only on the two closest public-pattern source shapes:

- Agent Action Boundary Benchmark-style action drift
- AgentShield-Bench-style MCP/tool-call safety

The point is to keep moving if no outside reviewer provides metadata, while still making replacement metadata the next validation ask.

## Run

```bash
python -m reference_engine.public_fallback_adapter --pretty
```

Generated outputs:

- `examples/public_fallback_adapter_normalized_customer_eval_actions.json`
- `reports/Public_Fallback_Adapter_Report.md`
- `reports/public_fallback_adapter_report.json`
- `reports/public_fallback_adapter_customer_evaluation/Customer_Evaluation_Report.md`
- `reports/public_fallback_adapter_customer_evaluation/customer_evaluation_report.json`

## What It Does

The adapter maps six public-pattern rows into SMERC customer-evaluation metadata:

- three action-boundary rows
- three MCP/tool-call safety rows

It then runs the same SMERC customer-evaluation path used by company reviewers.

## What It Asks Next

> Can you replace these six public-pattern rows with 5 to 25 metadata-only actions from one real workflow and label whether the SMERC posture is useful, too strict, too loose, irrelevant, or unclear?

## Evidence Boundary

This is not an official benchmark score, customer validation, production proof, incident-reduction evidence, or endorsement from any source project.

Do not copy upstream raw prompts, canary secrets, traces, customer data, proprietary rows, or operational exploit payloads into SMERC.
