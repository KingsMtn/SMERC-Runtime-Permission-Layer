# SMERC-F Fortune 500 Financial Services Review

## Purpose

This packet gives financial-services reviewers a safe way to evaluate SMERC-F without treating it as a payment system, trading system, custody product, AML system, compliance platform, or production-certified financial control.

SMERC-F is a financial-action governance profile for SMERC. It asks whether a proposed automated financial action is recoverable, reviewable, and structurally defensible before execution.

The review posture is intentionally conservative:

```text
metadata-only action examples -> SMERC-F shadow-mode scoring -> reviewer comparison -> evidence report
```

Do not connect SMERC-F to live funds, wallets, settlement rails, customer records, suspicious-activity files, production payment execution, or irreversible financial operations during a first review.

## Enterprise Positioning

Financial institutions already have identity, access control, fraud monitoring, AML, sanctions screening, model risk governance, change management, incident response, audit, and human approval workflows.

SMERC-F does not replace those controls.

SMERC-F adds a pre-execution question that is often missing from authorized automation:

> If this automated financial action is technically allowed, is it recoverable enough to proceed now?

This matters when an action may be authorized but still operationally unsafe because rollback is slow, containment is weak, evidence is incomplete, confidence is deteriorating, counterparty exposure is concentrated, or the downstream execution path is difficult to unwind.

## Reviewers

The strongest Fortune 500 financial-services review group includes:

- CISO or deputy CISO
- Head of payments risk
- Head of treasury operations
- Head of AI governance
- model risk or operational risk owner
- financial-crime technology owner
- platform engineering or DevSecOps lead
- legal, privacy, or data-handling reviewer
- architecture review owner

The first reviewer does not need to be the final buyer. The first useful reviewer is the person who can say whether recoverability scoring would change review behavior on real automated financial actions.

## Candidate Workflows

Good first-review workflow families include:

| Workflow | Why SMERC-F may matter | First-review boundary |
| --- | --- | --- |
| Refund release automation | Refunds may be valid but difficult to claw back at scale. | Metadata-only examples with amount band, evidence state, reversal window, and approval path. |
| Payment release or hold | Payment authorization does not answer recoverability after release. | No raw payment payloads, customer records, account numbers, or live rails. |
| Treasury rebalance | Internal movement may still amplify liquidity or concentration stress. | Synthetic or normalized treasury-action metadata. |
| Stablecoin redemption review | Settlement finality and liquidity imbalance can create hard-to-reverse exposure. | No wallet keys, customer identities, or live reserve instructions. |
| Digital-asset withdrawal review | Authorized withdrawals may be irreversible after execution. | Metadata-only action description with custody and reversal assumptions. |
| Transaction-limit change | Limit changes can expand downstream blast radius. | Policy metadata, scope, duration, and approval state only. |
| Collateral or counterparty limit update | Correct-looking changes can concentrate exposure. | Risk-category metadata without confidential counterparty files. |
| AI-assisted financial operations | Agent actions can combine speed, uncertainty, and tool authority. | Agent/tool metadata, proposed action, and reviewer label only. |

## Reference Architecture

```text
Financial workflow or AI agent
        |
        v
Action metadata boundary
        |
        v
Runtime Evidence Trust Gate
        |
        v
SMERC-F financial-action profile
        |
        v
ALLOW / THROTTLE / FREEZE / DENY / ESCALATE
        |
        v
SPARTa route and controls
        |
        v
Decision Lifecycle Ledger and governance report
        |
        v
Reviewer comparison and pilot evidence
```

In a first review, SMERC-F should score proposed actions in shadow mode. Existing financial controls remain the source of truth for actual execution.

## What SMERC-F Returns

For each action, SMERC-F should return:

- posture: `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE`
- irreversible exposure score
- reversible capacity score
- confidence or signal-risk score
- driver codes
- recommended controls
- SPARTa route recommendation
- replay identifier
- decision hash
- governance report reference
- Decision Lifecycle Ledger evidence where available

Financial reviewers should focus on whether the posture is useful, not whether the reference thresholds are already institution-calibrated.

## Data Boundary

Use metadata-only action examples for the first review.

Acceptable example fields:

- action category
- actor type
- automation type
- amount band or scope band
- current policy outcome
- review path
- reversibility estimate
- rollback or reversal latency band
- evidence-validity estimate
- anomaly estimate
- impact scope
- counterparty concentration band
- liquidity stress indicator
- reviewer label

Do not provide:

- customer names or account identifiers
- wallet private keys or seed phrases
- production credentials or secrets
- raw transaction payloads
- suspicious-activity report content
- sanctions-screening records
- confidential model prompts
- regulated customer records
- live execution instructions
- private incident records without legal approval

## Pilot Design

Start with one workflow family and one review team.

### Week Zero

- confirm workflow owner
- confirm security owner
- confirm data boundary
- confirm metadata-only sample format
- confirm stop conditions
- select 10 to 25 representative action examples
- run the SMERC-F benchmark and profile packet
- agree on reviewer labels and success metrics

### Weeks One Through Four

- score sampled actions in shadow mode
- collect reviewer labels
- compare SMERC-F posture to current review outcome
- capture where `THROTTLE`, `FREEZE`, or `ESCALATE` adds useful signal
- identify false release candidates
- identify false restraint candidates
- record latency and evidence gaps
- generate weekly governance summaries

### Day 30 Decision

Choose one:

| Decision | Meaning |
| --- | --- |
| Stop | Recoverability scoring did not add useful signal. |
| Narrow | The workflow or metadata boundary needs adjustment. |
| Continue shadow mode | More examples are needed before judgment. |
| Recommend mode | Show SMERC-F recommendations to reviewers while existing controls still decide execution. |

Do not move directly from first review to production enforcement.

## Success Metrics

The review is useful only if it produces measurable evidence.

Track:

- reviewer agreement rate
- false release candidates
- false restraint candidates
- useful restraint examples
- posture distribution
- percentage of technically allowed actions that SMERC-F restrains
- actions where `THROTTLE` is better than allow/block
- actions where `FREEZE` or `ESCALATE` improves accountability
- metadata fields most often missing
- median and p95 scoring latency
- reviewer time added or reduced
- controls recommended per workflow family

## Procurement And Legal Boundary

SMERC-F should be introduced as a shadow-mode evaluation artifact, not a production purchase.

The review should state:

- no live fund movement
- no customer data required for first review
- no production enforcement
- no regulatory compliance claim
- no AML replacement claim
- no sanctions-screening claim
- no custody, settlement, or payment execution claim
- no incident-reduction claim before customer evidence exists
- customer legal and security review required before sensitive data is shared

If sensitive workflows are discussed, use a customer-approved NDA and data-handling addendum before exchanging non-public workflow details.

## Evidence To Inspect

Start with:

- `docs/SMERC_F_Profile_Packet.md`
- `docs/SMERC_F_AML_Inspired_Spur.md`
- `docs/SMERC_F_Stablecoin_Blockchain_Pilot_Fit.md`
- `pilot_package/SMERC_F_Financial_Shadow_Mode_Pilot_Path.md`
- `docs/Runtime_Evidence_Trust_Gate.md`
- `docs/SPARTa_v2_Execution_Adapter_Framework.md`
- `docs/Decision_Lifecycle_Ledger.md`
- `docs/Governance_Report_Generator.md`
- `reports/SMERC_F_Profile_Packet.md`
- `reports/AML_Inspired_Financial_Governance_Benchmark.md`
- `reports/SMERC_F_Replay_Report.md`

Run:

```bash
python -m reference_engine.smerc_f_profile_packet examples/financial_action_requests.json --policies conservative balanced permissive --pretty
python -m reference_engine.aml_inspired_benchmark examples/aml_inspired_financial_governance_scenarios.json --pretty
python -m reference_engine.financial_replay examples/financial_replay_scenarios.json --pretty
```

## What Would Make A Fortune 500 Financial Company Say Yes

The review becomes commercially meaningful if reviewers say:

- "This catches actions our current allow/deny review treats too simply."
- "`THROTTLE` or `FREEZE` would have changed how we reviewed this action."
- "The metadata boundary is safe enough for a shadow-mode pilot."
- "This complements our existing controls rather than replacing them."
- "The governance report is useful for audit, model risk, or operational risk review."
- "We have a workflow where reversibility matters before execution."

## What Would Make Them Say No

Stop or narrow the effort if reviewers say:

- existing controls already capture recoverability clearly
- action metadata is not available before execution
- reviewers cannot label outcomes
- the workflow is not automated or becoming automated
- the organization wants regulatory AML or fraud replacement
- the first review would require sensitive data that legal or security cannot approve
- the scores do not change review behavior

## Bottom Line

SMERC-F is most credible for Fortune 500 financial services when it is framed as:

> recoverability-aware runtime governance for automated financial actions before execution.

It should be sold first as a metadata-only shadow-mode review, not as a production enforcement system. The goal is to prove whether recoverability scoring changes reviewer judgment on real financial-action workflows.
