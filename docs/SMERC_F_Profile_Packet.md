# SMERC-F Profile Packet

SMERC-F is a financial-action governance profile for SMERC. It evaluates proposed autonomous-capital actions before execution and returns restrained states such as `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE`.

SMERC-F is not a cryptocurrency, token, bank, broker-dealer, exchange, custodian, trading system, investment product, or production-certified financial control.

## Purpose

The profile packet gives reviewers a compact way to inspect:

- financial signal taxonomy
- policy profiles evaluated
- state distribution
- high-restraint outcomes
- driver codes
- controls and recommended actions
- commercial and compliance limits

## Example

```bash
python -m reference_engine.smerc_f_profile_packet examples/financial_action_requests.json --policies conservative balanced permissive --pretty --json-output reports/smerc_f_profile_packet.json --markdown-output reports/SMERC_F_Profile_Packet.md
```

## Signal Categories

- treasury
- settlement
- stablecoin
- counterparty
- market
- behavioral
- agent
- governance

## Proper Use

Use the packet for:

- technical review
- historical replay planning
- shadow-mode pilot design
- model-risk and governance discussion
- patent and product boundary review

Do not use the packet to claim:

- production readiness
- regulatory approval
- market prediction
- custody capability
- automated settlement authorization
- financial safety certification

## Relationship To Core SMERC

Core SMERC remains runtime permission infrastructure for AI agents and high-impact automated systems. SMERC-F demonstrates that the same action-boundary method can be applied to financial workflows, but the first commercial wedge remains GitHub Actions and AI-agent runtime governance.
