# SMERC-F External Financial Signals

## Purpose

SMERC-F can consume outputs from existing financial-risk and compliance systems as evidence before automated financial actions execute.

The purpose is narrow:

> Let AML/KYT, wallet-screening, fraud, treasury-risk, reserve-monitoring, Travel Rule, and smart-contract-risk tools remain the source systems while SMERC-F adds recoverability-aware pre-execution governance.

This is not AML compliance, sanctions screening, Travel Rule compliance, fraud detection, custody, settlement, payment execution, legal advice, or production certification.

## Why This Matters

Financial institutions already buy and operate systems that answer questions such as:

- is this wallet risky?
- is this transaction suspicious?
- is this beneficiary information incomplete?
- is this reserve or liquidity condition abnormal?
- is this smart contract or bridge route high risk?

SMERC-F adds a different question:

> Even with those signals available, is this automated financial action recoverable enough to execute now?

That difference is the product lane. SMERC-F should complement Chainalysis-, Elliptic-, TRM-, Circle-, Fireblocks-, fraud-, treasury-, and risk-style outputs rather than compete with them as the system of record.

## Financial Action Taxonomy

The external-signal adapter currently supports:

- `customer_refund_batch`
- `payment_release`
- `payment_retry`
- `treasury_rebalance`
- `stablecoin_mint`
- `stablecoin_burn`
- `stablecoin_redemption`
- `stablecoin_bridge_transfer`
- `wallet_permission_update`
- `tokenized_collateral_move`
- `transaction_limit_change`
- `reserve_status_publish`
- `smart_contract_admin_change`

## Supported Signal Families

- `blockchain_analytics`
- `transaction_monitoring`
- `wallet_screening`
- `travel_rule`
- `fraud_engine`
- `treasury_risk`
- `stablecoin_reserve_monitor`
- `smart_contract_risk`

## Run

```bash
python -m reference_engine.smerc_f_external_signals \
  examples/smerc_f_external_signal_examples.json \
  --pretty
```

Outputs:

```text
reports/SMERC_F_External_Signal_Report.md
reports/smerc_f_external_signal_report.json
```

## Work / Result / Impact Framing

Each record should be read as:

- Work: normalize external financial signals into SMERC-F recoverability fields.
- Result: return `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE` with exposure, capacity, drivers, controls, and a decision hash.
- Impact: identify where an action that is authorized or compliance-clear may still need restraint because recovery is weak.

## Evidence Boundary

This adapter demonstrates input shape, normalization, recoverability scoring, and report generation.

It does not:

- call vendor APIs
- perform AML or KYT screening
- determine sanctions status
- perform address attribution
- satisfy Travel Rule obligations
- move funds
- execute transactions
- update smart contracts
- replace custody controls
- certify compliance
- prove incident reduction

