# SMERC-F AML-Inspired Financial Governance Benchmark

Generated at: `2026-07-29T03:09:19+00:00`
Policy: `balanced`

## Purpose

This benchmark compares an AML-style `CLEAR` / `ALERT` lens with SMERC-F recoverability-aware financial action governance.

It does not test whether SMERC-F can detect money laundering. It tests whether recoverability scoring produces different governance postures for financial actions that may be authorized, suspicious, reversible, irreversible, constrained, or review-worthy.

## Evidence Boundary

AML-inspired benchmark only. It is not AML software, sanctions screening, suspicious-activity reporting, regulatory compliance, customer validation, production certification, or incident-reduction proof.

## Summary

- Scenarios: `8`
- AML baseline counts: `{'CLEAR': 4, 'ALERT': 4}`
- SMERC-F state counts: `{'ALLOW': 2, 'THROTTLE': 4, 'FREEZE': 1, 'DENY': 0, 'ESCALATE': 1}`
- Recoverability delta count: `2`
- Recoverability delta rate: `0.25`

## Delta Types

| Delta | Count | Meaning |
| --- | ---: | --- |
| `AML_ALERT_SMERC_RESTRAINT` | 4 | Both lenses indicate review or restraint, but for different reasons: suspiciousness versus recoverability and execution risk. |
| `AML_CLEAR_SMERC_ALLOW` | 2 | Both lenses allow the action under the reference scenario. |
| `AML_CLEAR_SMERC_RESTRAINT` | 2 | AML-style suspiciousness is clear, but SMERC-F restrains the action because recoverability or financial-operational exposure is weak. |

## Scenario Results

| Scenario | AML | SMERC-F | Exposure | Capacity | Delta |
| --- | --- | --- | ---: | ---: | --- |
| `AML_ROUTINE_VENDOR_PAYMENT` | `CLEAR` | `ALLOW` | 0.188 | 0.795 | `AML_CLEAR_SMERC_ALLOW` |
| `AML_APPROVED_WIRE_WEAK_REVERSAL` | `CLEAR` | `ALLOW` | 0.425 | 0.526 | `AML_CLEAR_SMERC_ALLOW` |
| `AML_REFUND_BATCH_SPIKE` | `ALERT` | `THROTTLE` | 0.46 | 0.495 | `AML_ALERT_SMERC_RESTRAINT` |
| `AML_CRYPTO_WITHDRAWAL_NEW_DEVICE` | `ALERT` | `FREEZE` | 0.684 | 0.251 | `AML_ALERT_SMERC_RESTRAINT` |
| `AML_ALERT_BUT_RECOVERABLE_LIMIT_CHANGE` | `ALERT` | `THROTTLE` | 0.237 | 0.793 | `AML_ALERT_SMERC_RESTRAINT` |
| `AML_TREASURY_REBALANCE_MARKET_STRESS` | `CLEAR` | `THROTTLE` | 0.59 | 0.562 | `AML_CLEAR_SMERC_RESTRAINT` |
| `AML_RELEASE_FROZEN_PAYMENT_OVERRIDE` | `ALERT` | `ESCALATE` | 0.585 | 0.354 | `AML_ALERT_SMERC_RESTRAINT` |
| `AML_STABLECOIN_REDEMPTION_IMBALANCE` | `CLEAR` | `THROTTLE` | 0.668 | 0.47 | `AML_CLEAR_SMERC_RESTRAINT` |

## Demo-Ready Examples

### AML_CRYPTO_WITHDRAWAL_NEW_DEVICE

- Category: `digital_asset_withdrawal`
- AML baseline: `ALERT` because Withdrawal request combines new device behavior, high velocity, and new destination risk.
- SMERC-F state: `FREEZE`
- Irreversible exposure: `0.684`
- Reversible capacity: `0.251`
- Drivers: `['AGENT_VELOCITY', 'SETTLEMENT_ANOMALY', 'COUNTERPARTY_CONCENTRATION', 'MODEL_DISAGREEMENT', 'AUTHORIZATION_SUPPORT_WEAK', 'EVIDENCE_VALIDITY_WEAK', 'LOW_REVERSIBILITY']`
- Controls: `['pause_automation', 'preserve_state', 'secondary_validation', 'supervisor_review']`
- Interpretation: Both lenses indicate review or restraint, but for different reasons: suspiciousness versus recoverability and execution risk.

### AML_STABLECOIN_REDEMPTION_IMBALANCE

- Category: `stablecoin_redemption`
- AML baseline: `CLEAR` because Institutional redemption request is from a known customer and passes ordinary identity and sanctions checks.
- SMERC-F state: `THROTTLE`
- Irreversible exposure: `0.668`
- Reversible capacity: `0.47`
- Drivers: `['STABLECOIN_IMBALANCE', 'LIQUIDITY_CONCENTRATION', 'MARKET_INSTABILITY', 'AGENT_VELOCITY', 'COUNTERPARTY_CONCENTRATION', 'LOW_REVERSIBILITY']`
- Controls: `['reduce_transaction_size', 'lower_velocity', 'require_dual_approval', 'log_replay']`
- Interpretation: AML-style suspiciousness is clear, but SMERC-F restrains the action because recoverability or financial-operational exposure is weak.

### AML_TREASURY_REBALANCE_MARKET_STRESS

- Category: `treasury_rebalance`
- AML baseline: `CLEAR` because Internal treasury reallocation is between approved accounts and does not indicate suspicious customer behavior.
- SMERC-F state: `THROTTLE`
- Irreversible exposure: `0.59`
- Reversible capacity: `0.562`
- Drivers: `['MARKET_INSTABILITY', 'LIQUIDITY_CONCENTRATION', 'AGENT_VELOCITY', 'COLLATERAL_STRESS', 'COUNTERPARTY_CONCENTRATION', 'LOW_REVERSIBILITY']`
- Controls: `['reduce_transaction_size', 'lower_velocity', 'require_dual_approval', 'log_replay']`
- Interpretation: AML-style suspiciousness is clear, but SMERC-F restrains the action because recoverability or financial-operational exposure is weak.

### AML_RELEASE_FROZEN_PAYMENT_OVERRIDE

- Category: `frozen_payment`
- AML baseline: `ALERT` because Releasing a previously frozen payment requires analyst review and documented rationale.
- SMERC-F state: `ESCALATE`
- Irreversible exposure: `0.585`
- Reversible capacity: `0.354`
- Drivers: `['SETTLEMENT_ANOMALY', 'COUNTERPARTY_CONCENTRATION', 'AGENT_VELOCITY', 'MODEL_DISAGREEMENT', 'AUTHORIZATION_SUPPORT_WEAK', 'EVIDENCE_VALIDITY_WEAK', 'LOW_REVERSIBILITY']`
- Controls: `['route_to_accountable_reviewer', 'require_explicit_approval', 'preserve_replay']`
- Interpretation: Both lenses indicate review or restraint, but for different reasons: suspiciousness versus recoverability and execution risk.

### AML_REFUND_BATCH_SPIKE

- Category: `refunds`
- AML baseline: `ALERT` because Refund volume and velocity exceed normal queue behavior and require analyst review.
- SMERC-F state: `THROTTLE`
- Irreversible exposure: `0.46`
- Reversible capacity: `0.495`
- Drivers: `['AGENT_VELOCITY', 'SETTLEMENT_ANOMALY', 'LOW_REVERSIBILITY']`
- Controls: `['reduce_transaction_size', 'lower_velocity', 'require_dual_approval', 'log_replay']`
- Interpretation: Both lenses indicate review or restraint, but for different reasons: suspiciousness versus recoverability and execution risk.

## Commercial Interpretation

AML is the familiar enterprise pattern: risk scoring, alert queues, analyst review, evidence, and auditability. SMERC-F borrows that operating pattern but applies it to pre-execution financial actions. The core question is not whether an action is suspicious; it is whether automated execution is recoverable, reviewable, and structurally defensible now.
