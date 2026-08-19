# Fortune 500 Financial Services Review Checklist

## Purpose

Use this checklist before offering SMERC-F to a large financial-services company. The goal is to confirm whether a safe metadata-only review is possible.

## Qualification

The prospect is a strong fit only if all of these are true:

- automated financial actions exist or are being planned
- at least one action can create hard-to-reverse consequences
- a review team can compare SMERC-F posture with human judgment
- the first review can run in shadow mode
- metadata-only examples are available
- the prospect understands SMERC-F is not AML, fraud detection, custody, settlement, trading, or payment execution

## Required Owners

- executive sponsor or senior risk/security owner
- workflow owner
- technical owner
- reviewer group
- data-handling approver
- legal or procurement contact if non-public details are shared

## Safe First Scope

Choose one:

- refund release
- payment release or hold
- treasury rebalance
- stablecoin redemption review
- digital-asset withdrawal review
- transaction-limit change
- counterparty exposure update
- AI-assisted financial operation

Reject first scopes that require live fund movement, production credentials, customer records, private wallet material, raw regulated transaction payloads, or confidential suspicious-activity records.

## Data Boundary Gate

Before any review, confirm:

- no customer identifiers
- no account numbers
- no wallet private keys
- no production secrets
- no raw transaction payloads
- no suspicious-activity report content
- no sanctions-screening records
- no live execution instructions
- no private incident records without legal approval

## Evidence Package

Provide reviewers:

- `docs/SMERC_F_Fortune_500_Financial_Services_Review.md`
- `docs/SMERC_F_Profile_Packet.md`
- `pilot_package/SMERC_F_Financial_Shadow_Mode_Pilot_Path.md`
- `reports/SMERC_F_Profile_Packet.md`
- `reports/AML_Inspired_Financial_Governance_Benchmark.md`
- `reports/SMERC_F_Replay_Report.md`

## Success Metrics

Track:

- reviewer agreement rate
- false release candidates
- false restraint candidates
- useful `THROTTLE` decisions
- useful `FREEZE` decisions
- useful `ESCALATE` decisions
- metadata gaps
- posture distribution
- median and p95 evaluation latency
- reviewer time impact
- decision-report usefulness

## Stop Conditions

Stop or narrow if:

- the workflow is not automated
- recoverability does not change review behavior
- safe metadata cannot be provided
- reviewer labels are unavailable
- the prospect wants production enforcement immediately
- the prospect expects AML, fraud, sanctions, custody, settlement, or payment execution

## First Offer

Offer:

> A 30-day metadata-only SMERC-F shadow-mode review for one automated financial workflow family.

Do not offer:

> Production enforcement for financial actions.

Do not claim:

> SMERC-F is production-certified, compliance-attested, or proven to reduce financial incidents.
