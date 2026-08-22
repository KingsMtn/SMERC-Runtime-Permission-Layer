# SMERC MCP Governance Gateway

## Purpose

The SMERC MCP Governance Gateway is the infrastructure layer that sits in front of MCP tool calls.

It combines:

- MCP tool registry
- runtime SMERC posture scoring
- SPARTa route behavior
- loop and velocity pressure
- cost-unit metering
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

## Why It Comes Before More SMERC-F

SMERC-F is a financial-services profile.

The gateway is where SMERC belongs in the action path:

```text
agent or automation
-> MCP tool call
-> SMERC MCP Governance Gateway
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
- payment rails
- x402
- wallet settlement
- prompt-injection defense
- sandboxing
- SIEM export
- production billing

Those are later enterprise integration concerns. The first proof is whether the gateway can produce useful pre-execution posture, pressure detection, and replay evidence for MCP tool calls.
