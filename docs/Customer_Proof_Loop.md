# SMERC Customer Proof Loop

The customer proof loop is the fastest way to show that SMERC is software, not only positioning material.

It runs one governed action through the current runtime path:

1. Runtime admission gate
2. Recoverability scoring
3. SPARTa route generation
4. Decision Lifecycle Ledger record
5. Markdown and JSON evidence report

Run it locally:

```bash
python -m reference_engine.customer_proof_loop examples/customer_proof_action.json --output-dir reports/customer_proof_loop --pretty
```

The command writes:

- `reports/customer_proof_loop/customer_proof_loop.json`
- `reports/customer_proof_loop/Customer_Proof_Loop_Report.md`

## What It Proves

The loop verifies four concrete conditions:

- Hard runtime gates passed before recoverability scoring.
- Recoverability scoring permits progression only when evidence and recovery capacity are sufficient.
- SPARTa can translate the posture into an executable or blocked route.
- The Decision Lifecycle Ledger is hash-verifiable.

If hard runtime gates fail, recoverability scoring is skipped and the request fails closed. This is deliberate. Recoverability scoring must not rescue invalid identity, invalid permits, malformed tool contracts, weak attestations, or missing required evidence.

## Customer Use

For a first pilot conversation, a company can replace `examples/customer_proof_action.json` with one of its own synthetic actions:

- A GitHub Actions deployment
- A cloud administration task
- An MCP tool call
- A financial workflow action
- A security automation action

The output bundle gives reviewers a replayable artifact rather than a slide-only explanation.

## Current Boundary

This proof loop does not execute a customer workflow. It evaluates declared metadata and produces a route plus evidence bundle. Production pilots still require customer-owned integration work for identity, permissions, tool contracts, execution adapters, and audit storage.
