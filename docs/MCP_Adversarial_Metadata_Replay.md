# MCP Adversarial Metadata Replay

## Purpose

This replay pack tests SMERC against current MCP security pain points without committing exploit payloads.

It answers a reviewer question:

> If MCP tool metadata, nested schemas, server instructions, cached manifests, or recoverability evidence are untrusted or missing, does SMERC fail closed before execution?

## Run

```bash
python -m reference_engine.mcp_adversarial_metadata_replay examples/mcp_adversarial_metadata.json --pretty
```

Generated outputs:

- `examples/mcp_adversarial_normalized_customer_eval_actions.json`
- `reports/MCP_Adversarial_Metadata_Replay_Report.md`
- `reports/mcp_adversarial_metadata_replay_report.json`
- `reports/mcp_adversarial_customer_evaluation/Customer_Evaluation_Report.md`
- `reports/mcp_adversarial_customer_evaluation/customer_evaluation_report.json`

## Surfaces Covered

- tool description poisoning
- nested schema poisoning
- server instructions injection
- public cache poisoning
- schema drift after approval
- benign tool with dangerous arguments
- encoded instruction evasion
- missing recoverability evidence

## Work / Result / Impact

Work: convert public MCP security discussion themes into safe metadata-only action records.

Result: SMERC evaluates each record through hard gates, recoverability scoring, Governance Routing Workbench routing, autonomy budgeting, and Decision Lifecycle Ledger evidence.

Impact: reviewers can see that SMERC is not only a scanner. It is a pre-execution decision layer that treats tool metadata as untrusted, separates static contract checks from runtime recoverability evidence, and prevents missing evidence from quietly becoming permission.

## Evidence Boundary

This is not an official MCP benchmark score, vulnerability disclosure, customer pilot, compliance claim, or proof that every encoded or foreign-language prompt-injection variant is caught.

It is a safe replay of failure shapes discussed publicly by MCP and AI-agent security communities.

## Reviewer Question

Which MCP failure shape should be tested next with a live proxy trace: nested schema poisoning, server instructions injection, schema drift, encoded instructions, or missing recoverability evidence?
