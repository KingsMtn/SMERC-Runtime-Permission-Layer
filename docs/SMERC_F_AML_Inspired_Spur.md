# SMERC-F AML-Inspired Financial Governance Spur

## Purpose

SMERC-F should be understood as an AML-inspired financial-action governance profile, not as AML software.

AML systems ask whether behavior is suspicious, reportable, or requires compliance review.

SMERC-F asks whether an automated financial action is recoverable, reviewable, and structurally defensible before execution.

## Positioning

> SMERC-F brings AML-style review discipline to AI-driven financial actions, but its scoring lens is recoverability before execution.

This is useful because a financial action can be:

- authorized but hard to reverse
- not suspicious but operationally dangerous
- suspicious but technically recoverable under constraints
- legitimate but missing enough evidence for automated release
- suitable for throttling or escalation instead of a simple allow/block answer

## What SMERC-F Borrows From AML

- risk scoring
- alert/review queues
- analyst-style case review
- reason codes
- audit evidence
- threshold calibration
- false positive and false negative measurement
- reviewer override tracking

## What SMERC-F Does Not Claim

SMERC-F does not provide:

- anti-money-laundering compliance
- sanctions screening
- suspicious activity report filing
- know-your-customer verification
- transaction monitoring certification
- regulatory reporting
- custody, settlement, or payment execution

Those remain the responsibility of existing AML, fraud, compliance, banking, payment, custody, and legal systems.

## Benchmark

Run:

```bash
python -m reference_engine.aml_inspired_benchmark \
  examples/aml_inspired_financial_governance_scenarios.json \
  --pretty
```

Generated outputs:

```text
reports/AML_Inspired_Financial_Governance_Benchmark.md
reports/aml_inspired_financial_governance_benchmark.json
```

## What The Benchmark Shows

The benchmark compares:

- AML-style `CLEAR` / `ALERT`
- SMERC-F `ALLOW` / `THROTTLE` / `FREEZE` / `DENY` / `ESCALATE`

The key metric is the recoverability delta: scenarios where the AML-style lens and SMERC-F lens produce meaningfully different operating postures.

The most important class is:

```text
AML_CLEAR_SMERC_RESTRAINT
```

This means the action may not look suspicious under an AML-style baseline, but SMERC-F still restrains automated execution because recoverability or operational exposure is weak.

## Commercial Use

Use this spur for conversations with:

- fintech risk teams
- payment operations teams
- treasury operations teams
- crypto compliance teams
- banking innovation teams
- financial platform security teams

Do not lead with SMERC-F before the core GitHub Actions pilot path is understandable. SMERC-F is a domain expansion proof, not the first broad product wedge.

For stablecoin, blockchain, payment, treasury, and tokenized-finance fit, see `docs/SMERC_F_Stablecoin_Blockchain_Pilot_Fit.md`.
