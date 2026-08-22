# SMERC MCP Governance Gateway Report

Generated: `2026-08-22T02:30:00+00:00`

## Executive Summary

- Mode: `enforce`
- Session: `mcp_gateway_reference_session_001`
- Registry: `mcp_gateway_registry_reference_v1`
- Requests evaluated: `4`
- Registered tools: `3`
- Cumulative cost units: `11.2`
- Forwarded calls: `1`
- Blocked or held calls: `3`

## Posture Distribution

- `ALLOW`: `1`
- `DENY`: `3`

## Proxy Actions

- `block_tool_call`: `3`
- `forward_tool_call`: `1`

## Highest Pressure Calls

| Request | Tool | Profile | Pressure | Posture | Proxy Action | Drivers |
| --- | --- | --- | ---: | --- | --- | --- |
| `MCP_STABLECOIN_TRANSFER_004` | `finance_ops_mcp.stablecoin_treasury_transfer` | `smerc_f` | 0.78 | `DENY` | `block_tool_call` | session_budget_pressure, scope_exceeds_registry_limit, high_risk_tool_tier |
| `MCP_DELETE_CUSTOMER_RECORDS_002` | `customer_data_mcp.delete_customer_records` | `customer_data` | 0.7 | `DENY` | `block_tool_call` | scope_exceeds_registry_limit, high_risk_tool_tier |
| `MCP_STABLECOIN_TRANSFER_003` | `finance_ops_mcp.stablecoin_treasury_transfer` | `smerc_f` | 0.62 | `DENY` | `block_tool_call` | scope_exceeds_registry_limit, high_risk_tool_tier |
| `MCP_SEARCH_DOCS_001` | `knowledge_mcp.search_documents` | `general` | 0.05 | `ALLOW` | `forward_tool_call` | none |

## Decision Table

| # | Request | Tool | Profile | Posture | Route | Proxy Action | Forward |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | `MCP_SEARCH_DOCS_001` | `knowledge_mcp.search_documents` | `general` | `ALLOW` | `EXECUTE` | `forward_tool_call` | `true` |
| 2 | `MCP_DELETE_CUSTOMER_RECORDS_002` | `customer_data_mcp.delete_customer_records` | `customer_data` | `DENY` | `BLOCK` | `block_tool_call` | `false` |
| 3 | `MCP_STABLECOIN_TRANSFER_003` | `finance_ops_mcp.stablecoin_treasury_transfer` | `smerc_f` | `DENY` | `BLOCK` | `block_tool_call` | `false` |
| 4 | `MCP_STABLECOIN_TRANSFER_004` | `finance_ops_mcp.stablecoin_treasury_transfer` | `smerc_f` | `DENY` | `BLOCK` | `block_tool_call` | `false` |

## Commercial Boundary

This gateway package demonstrates MCP tool registry governance, repeated-call pressure, cost metering, and SMERC posture routing. It does not implement OAuth, mTLS, native MCP transport, payment rails, x402, wallet settlement, prompt-injection defense, sandboxing, SIEM export, or production billing.

## Recommended Next Action

Use this gateway in shadow mode against one MCP tool family, then compare SMERC posture, loop pressure, and reviewer labels before any enforcement or monetization work.
