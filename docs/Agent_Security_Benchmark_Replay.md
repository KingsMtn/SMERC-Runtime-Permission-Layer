# Agent Security Benchmark Replay

## Purpose

This replay maps Agent Security Benchmark-shaped metadata into SMERC's customer-evaluation path.

It is meant to answer:

> Can SMERC evaluate current AI-agent tool-use attack patterns before execution and return recoverability posture, Governance Routing Workbench route behavior, autonomy-budget impact, and Decision Lifecycle Ledger evidence?

## Source

- Source project: `https://github.com/vadimsv1/agent-security-benchmark`
- License observed: MIT
- Upstream shape: 30 prompts across exfiltration, stored prompt injection, privilege escalation, social engineering, multi-step escalation, and inconsistency probing.

The checked-in SMERC example does not commit the upstream raw prompts, host paths, secrets, raw tool transcripts, or generated attack artifacts. It uses metadata-only rows shaped from the public benchmark categories.

## Run It

```bash
python -m reference_engine.agent_security_benchmark_replay examples/agent_security_benchmark_metadata.json --pretty
```

Generated outputs:

- `examples/agent_security_benchmark_normalized_customer_eval_actions.json`
- `reports/Agent_Security_Benchmark_Replay_Report.md`
- `reports/agent_security_benchmark_replay_report.json`
- `reports/agent_security_benchmark_customer_evaluation/Customer_Evaluation_Report.md`
- `reports/agent_security_benchmark_customer_evaluation/customer_evaluation_report.json`

## What It Measures

- whether SMERC restrains expected tool-use attacks
- whether hard gates catch missing typed contracts, attestation, least privilege, or object-shape evidence
- whether `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE` give a more useful answer than simple allow/block
- which Governance Routing Workbench routes are produced before execution
- whether each decision can be preserved as valid Decision Lifecycle Ledger evidence

## Work / Result / Impact

Work: replay external AI-agent tool-use attack categories as safe metadata through SMERC.

Result: SMERC evaluates the rows through hard gates, recoverability scoring, Governance Routing Workbench routing, autonomy budgeting, and ledger evidence.

Impact: reviewers can inspect how SMERC behaves against current public agent-security benchmark shapes instead of only founder-created examples.

## Evidence Boundary

This is not an official Agent Security Benchmark score.

It is not an upstream runner result, production certification, customer validation, incident-reduction evidence, or proof that SMERC outperforms MCPGuard or any other tool.

Official comparison requires:

- upstream dataset version or commit
- documented upstream runner
- exact row inclusion criteria
- model and agent runtime configuration
- SMERC policy/profile version
- latency and overhead measurement
- skipped-row handling
- human label review where applicable

