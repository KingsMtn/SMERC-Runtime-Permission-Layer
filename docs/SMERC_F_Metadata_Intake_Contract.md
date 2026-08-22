# SMERC-F Metadata Intake Contract

## Purpose

This contract defines the safest first data boundary for a SMERC-F financial-services review.

It is designed for banks, fintechs, stablecoin operators, treasury teams, payment teams, blockchain infrastructure teams, and AI governance teams that want to evaluate recoverability-aware runtime permissioning without exposing live regulated data or production execution authority.

The first SMERC-F pilot should answer one question:

> Can metadata about proposed automated financial actions help reviewers decide whether an action should be allowed, throttled, frozen, denied, or escalated before execution?

## First Pilot Boundary

The first pilot must remain:

```text
metadata-only
shadow-mode
one workflow family
no production enforcement
no live fund movement
```

Existing financial controls remain the source of truth. SMERC-F provides a recoverability posture and evidence packet for reviewer comparison.

## Required Intake Fields

Each submitted record should describe a proposed automated action, not a completed private transaction payload.

| Field | Type | Purpose |
| --- | --- | --- |
| `record_id` | string | Stable customer-side identifier for replay and reviewer labels. |
| `workflow_family` | string | Bounded workflow category such as treasury_transfer, refund_approval, liquidity_rebalance, stablecoin_redemption, or deployment_finance_control. |
| `proposed_action` | string | Plain-language action the automated system wants to take. |
| `actor_type` | string | Who or what proposed the action: ai_agent, workflow_bot, treasury_system, payment_system, security_automation, or human_operator. |
| `existing_control_outcome` | string | Current system posture such as allow, review, alert, block, approval_required, or manual_only. |
| `amount_band_usd` | string | Band only, such as under_10k, 10k_100k, 100k_1m, 1m_10m, over_10m. Do not submit exact customer amounts in the first review. |
| `asset_type` | string | stablecoin, fiat, tokenized_deposit, treasury_asset, crypto_asset, internal_ledger_entry, or other. |
| `settlement_finality` | number | 0.0 to 1.0 estimate of how difficult the action is to reverse after settlement. |
| `rollback_latency` | number | 0.0 to 1.0 normalized time pressure where higher means slower rollback. |
| `containment_strength` | number | 0.0 to 1.0 estimate of scope limits, kill switches, hold periods, or circuit breakers. |
| `evidence_quality` | number | 0.0 to 1.0 completeness of available evidence at decision time. |
| `anomaly_pressure` | number | 0.0 to 1.0 anomaly, velocity, or pattern pressure relevant to the proposed action. |
| `counterparty_concentration` | number | 0.0 to 1.0 concentration or correlation pressure. |
| `market_stress` | number | 0.0 to 1.0 market, liquidity, redemption, collateral, or network stress. |
| `customer_impact_radius` | string | none, single_customer, limited_segment, broad_segment, enterprise_wide, or external_market. |
| `reviewer_label` | string | Optional human reviewer result after SMERC-F posture is shown: agree, disagree, override_safer, override_riskier, needs_more_data. |

## Optional Context Fields

These fields can improve review quality, but they should still be metadata-only.

- `source_system`
- `source_event_type`
- `policy_version`
- `model_version`
- `approval_status`
- `dual_control_available`
- `hold_period_available`
- `lawful_order_dependency`
- `issuer_or_custody_dependency`
- `redemption_pressure`
- `liquidity_concentration`
- `collateral_stress`
- `jurisdiction_complexity`
- `disclosure_gap`

## Prohibited First-Pilot Inputs

Do not submit:

- customer names
- account numbers
- wallet private keys
- seed phrases
- secrets
- access tokens
- raw regulated transaction payloads
- suspicious activity reports
- sanctions-screening results tied to identifiable parties
- full wallet address books
- exact customer balances
- production credentials
- executable fund-movement instructions
- instructions that could trigger live settlement, custody, or payment execution

## Example Intake Record

```json
{
  "record_id": "pilot-treasury-transfer-001",
  "workflow_family": "treasury_transfer",
  "proposed_action": "Automated treasury workflow proposes a stablecoin transfer from an operating wallet to an external liquidity venue.",
  "actor_type": "treasury_system",
  "existing_control_outcome": "allow",
  "amount_band_usd": "1m_10m",
  "asset_type": "stablecoin",
  "settlement_finality": 0.86,
  "rollback_latency": 0.78,
  "containment_strength": 0.42,
  "evidence_quality": 0.74,
  "anomaly_pressure": 0.51,
  "counterparty_concentration": 0.66,
  "market_stress": 0.48,
  "customer_impact_radius": "limited_segment",
  "dual_control_available": true,
  "hold_period_available": false,
  "reviewer_label": "needs_more_data"
}
```

## SMERC-F Output

For each record, SMERC-F should return:

- posture: `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE`
- irreversible exposure score
- reversible capacity score
- confidence or evidence sufficiency score
- reason codes
- recommended controls
- replay ID
- reviewer questions
- pilot boundary note

## Reviewer Questions

For each reviewed action, ask:

- Would this posture have changed how your team reviewed the action?
- Did SMERC-F identify a recoverability issue your current controls do not explicitly score?
- Was the posture too permissive, too restrictive, or useful?
- Which metadata field was missing?
- Which control would have made the action more recoverable?
- Should this action ever move from observe mode to recommend mode?

## Success Metrics

The first pilot should measure:

- reviewer agreement rate
- useful restraint rate
- false release candidates
- false restraint candidates
- metadata gap frequency
- posture distribution
- average reviewer time impact
- p50 and p95 scoring latency
- number of actions where recoverability changed the discussion

## Claim Boundary

This contract does not make SMERC-F:

- AML compliance
- legal compliance
- fraud detection
- sanctions screening
- custody software
- settlement infrastructure
- payment execution
- trading infrastructure
- production certification

The contract only defines a safe first metadata boundary for evaluating whether recoverability scoring is useful before automated financial actions execute.
