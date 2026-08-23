# SMERC MCP Governance Gateway

## Purpose

The SMERC MCP Governance Gateway is the infrastructure layer that sits in front of MCP tool calls.

It combines:

- MCP tool registry
- runtime SMERC posture scoring
- SPARTa route behavior
- deterministic ref-gate checks for typed contracts, attestation, least privilege, and expected object shape
- loop and velocity pressure
- cost-unit metering
- Autonomy Budgeting for current action, scope, risk-spend, and tool-tier allowance
- Decision Lifecycle Ledger evidence from the MCP proxy runner
- SMERC-F financial profile support for financial tool families

The gateway is the general product surface. SMERC-F is a domain profile that can run through it.

## Run

```bash
python -m reference_engine.mcp_governance_gateway --mode enforce --pretty
```

Outputs:

```text
reports/MCP_Governance_Gateway_Report.md
reports/mcp_governance_gateway_report.json
```

## What It Demonstrates

The reference session evaluates:

- a low-risk document search tool call
- a destructive customer-data deletion tool call
- two SMERC-F stablecoin treasury-transfer tool calls

The gateway tracks repeated calls, scope pressure, high-risk tool tiers, and cumulative session cost units before calling the existing MCP proxy runner.

It also checks whether the proposed call passes a deterministic ref gate:

- `typed_contract_valid`
- `attestation_valid`
- `least_privilege_confirmed`
- `object_shape_expected`

If a required ref-gate field is false, the gateway fails closed before recoverability can soften the decision. The report records the failing driver, raises pressure to `1.0`, and caps confidence and evidence validity.

The generated report also includes an Autonomy Budget summary. That summary shows whether the session still has available action budget, scope budget, risk budget, and tool-tier authority after the evaluated call sequence.

## Why It Comes Before More SMERC-F

SMERC-F is a financial-services profile.

The gateway is where SMERC belongs in the action path:

```text
agent or automation
-> MCP tool call
-> SMERC MCP Governance Gateway
-> ref-gate validation
-> SMERC posture
-> SPARTa route
-> proxy response
-> ledger evidence
-> optional execution
```

This keeps SMERC-F from becoming a separate branch. Financial actions become one governed tool family inside the same runtime gateway.

## What It Is Not

The gateway does not implement:

- OAuth
- mTLS
- native MCP transport
- typed-schema, object-validation, or least-privilege enforcement libraries
- payment rails
- x402
- wallet settlement
- prompt-injection defense
- sandboxing
- SIEM export
- production billing

Those are later enterprise integration concerns. The first proof is whether the gateway can produce useful pre-execution posture, deterministic fail-closed metadata checks, pressure detection, and replay evidence for MCP tool calls.

See also:

- `docs/SMERC_And_The_Ref_Pattern.md`
- `docs/Autonomy_Health_Framework.md`
- `docs/Autonomy_Budgeting_Framework.md`
