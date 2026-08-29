# SMERC-F Financial Reason Codes

## Purpose

SMERC-F is Financial Runtime Governance for automated financial actions. It adds a financial reason-code layer to the public-data replay so a reviewer can see why SMERC-F changed, confirmed, or restrained a proposed action.

This is not AML compliance, sanctions screening, fraud detection, custody, settlement, trading, payment execution, legal advice, or production financial-control certification.

## What It Adds

The replay already converts public-data-shaped stablecoin, blockchain, and incident records into SMERC-F action metadata. The reason-code layer adds a reviewer-friendly explanation beside each posture:

- what work was performed
- what result SMERC-F produced
- what impact that result may have before execution

## Reason Codes

| Code | Meaning |
| --- | --- |
| `AUTOMATION_VELOCITY_HIGH` | Automation speed is high enough that a bad action could compound before review. |
| `COUNTERPARTY_CONCENTRATION_HIGH` | Counterparty or recipient concentration creates a larger correlated exposure. |
| `FINANCIAL_EVIDENCE_WEAK` | The evidence available before execution is too thin for an automated financial action. |
| `GOVERNANCE_CHANGE_AUTHORITY_RISK` | A governance or authority-changing action may alter who can act later. |
| `LIQUIDITY_ROUTE_FRAGILE` | Liquidity and market stress suggest the action may not unwind cleanly. |
| `MARKET_STRESS_ELEVATED` | Market stress is high enough to make ordinary routing assumptions less reliable. |
| `REDEMPTION_PRESSURE_HIGH` | Stablecoin or reserve movement pressure suggests execution should slow or pause. |
| `REPORTED_ADDRESS_RISK` | A reported-address or incident signal should be preserved before action. |
| `SETTLEMENT_REVERSIBILITY_LOW` | Settlement finality or low reversibility limits recovery after execution. |
| `TOKENIZED_COLLATERAL_EXPOSURE_HIGH` | Collateral or tokenized-asset pressure raises the cost of acting too quickly. |

## Reviewer Question

The useful question for banks, fintechs, stablecoin operators, and treasury teams is:

> If existing systems allow, alert, review, or block an action, does recoverability evidence change whether automation should continue right now?

That is where SMERC-F is different. It does not replace identity, OPA, AML, fraud, blockchain analytics, case management, or approval tools. It consumes their signals and asks whether the proposed action is recoverable enough to proceed before execution.

## Run

```bash
python -m reference_engine.smerc_f_public_data_replay examples/smerc_f_public_data_replay_inputs.json --pretty
```

Outputs:

```text
reports/SMERC_F_Public_Data_Replay_Report.md
reports/smerc_f_public_data_replay_report.json
```

