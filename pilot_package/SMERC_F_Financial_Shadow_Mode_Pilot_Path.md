# SMERC-F Financial Shadow-Mode Pilot Path

## Purpose

This pilot path is for financial, stablecoin, payment, treasury, custody, or blockchain infrastructure teams that want to test SMERC-F without connecting it to live funds or production execution.

The first SMERC-F pilot should answer:

> Does recoverability-aware scoring add useful governance signal before automated financial actions execute?

This is not AML compliance, sanctions screening, payment execution, custody, settlement, or regulatory reporting.

## Starting Scope

Start with one workflow family in shadow mode:

- refund release
- payment release
- frozen-payment release
- stablecoin redemption review
- digital-asset withdrawal review
- treasury rebalance
- transaction-limit change
- counterparty exposure change

Do not start with live movement of funds. The first test should score metadata-only action examples and compare SMERC-F output against reviewer judgment.

## What The Customer Provides

- one financial workflow family
- one risk, compliance, security, or treasury owner
- one technical workflow owner
- reviewer group
- metadata-only action examples
- current allow/hold/review outcome where available
- weekly reviewer labels
- data boundary
- stop conditions

Do not provide wallet keys, production secrets, customer records, raw regulated transaction payloads, confidential suspicious-activity records, or live settlement instructions.

## What SMERC-F Provides

- financial action scoring
- AML-inspired benchmark comparison
- `ALLOW` / `THROTTLE` / `FREEZE` / `DENY` / `ESCALATE` posture
- irreversible exposure score
- reversible capacity score
- driver codes
- recommended controls
- decision hash
- replayable evidence report
- weekly metrics template
- final pilot recommendation

## Week Zero

Run the AML-inspired benchmark:

```bash
python -m reference_engine.aml_inspired_benchmark \
  examples/aml_inspired_financial_governance_scenarios.json \
  --pretty
```

Then review:

```text
reports/AML_Inspired_Financial_Governance_Benchmark.md
```

Proceed only if the prospect can name one workflow where recoverability matters before execution.

## Weeks One Through Four

Run shadow-mode scoring on sampled actions.

Collect:

- action count
- posture distribution
- AML-style baseline outcome where available
- SMERC-F state
- recoverability delta count
- reviewer agreement
- false release candidates
- false restraint candidates
- useful restraint examples
- override rate
- latency observations
- metadata quality notes

## 30-Day Decision

Choose one:

| Outcome | Meaning |
| --- | --- |
| Stop | Recoverability scoring did not add useful signal. |
| Narrow | The use case is real but the workflow or metadata boundary must change. |
| Continue shadow mode | More action volume is needed. |
| Move to recommend | Show SMERC-F recommendations to reviewers without blocking execution. |

Do not move to production enforcement from a first SMERC-F pilot.

## Success Criteria

The pilot is useful if reviewers can identify:

- actions that were technically allowed but hard to reverse
- actions where `THROTTLE` was better than allow/block
- actions where `FREEZE` or `ESCALATE` preserved accountability
- controls that would reduce blast radius
- metadata gaps that affect financial action governance

## Commercial Boundary

SMERC-F is a domain expansion path. It should not distract from the core GitHub Actions pilot unless a financial prospect has urgent recoverability pain and reviewer capacity.

The first commercial offer should be a limited financial shadow-mode pilot, not production enforcement.
