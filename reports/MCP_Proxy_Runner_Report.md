# SMERC MCP Proxy Runner Report

Generated: `2026-08-16T04:06:21+00:00`

## Proxy Decision

- Mode: `enforce`
- MCP request: `MCP_DELETE_CUSTOMER_RECORDS_001`
- Agent: `support_resolution_agent`
- Server: `customer_data_mcp`
- Tool: `delete_customer_records`
- Proxy action: `block_tool_call`
- Should forward tool call: `false`
- SMERC posture: `DENY`
- SPARTa route: `BLOCK`
- Replay ID: `replay_MCP_MCP_DELETE_CUSTOMER_RECORDS_001_1786853181649_12068616b0ac`

## Proxy Instructions

- Block the tool call.
- Preserve the replay and explain the denial.
- Require a materially safer new request before execution.

## Governance Report

# SMERC MCP Tool Governance Report

Generated: `2026-08-16T04:06:21+00:00`

## Summary

- MCP request: `MCP_DELETE_CUSTOMER_RECORDS_001`
- Agent: `support_resolution_agent`
- MCP server: `customer_data_mcp`
- Tool: `delete_customer_records`
- SMERC posture: `DENY`
- SPARTa route state: `BLOCK`
- Executable: `false`
- Recommended MCP result: `block_tool_call`

## Reason Codes

- `IRREVERSIBLE_EXPOSURE_HIGH`
- `RECOVERY_CAPACITY_LOW`
- `ROLLBACK_LATENCY_HIGH`
- `CANCEL_RELIABILITY_WEAK`
- `CONTAINMENT_WEAK`
- `IMPACT_SCOPE_WIDE`
- `EXTERNAL_SIDE_EFFECT`
- `SENSITIVE_DATA`

## Controls

- `block_execution`
- `preserve_replay`
- `explain_denial`

## Plain English

SMERC evaluated MCP tool `delete_customer_records` for agent `support_resolution_agent` and returned DENY. SPARTa mapped that posture to `BLOCK`, so an MCP client or proxy should use `block_tool_call` rather than blindly executing the tool call.

## Evidence Boundary

This adapter evaluates MCP tool-call metadata before execution. It does not implement MCP transport, OAuth, enterprise identity, sandboxing, prompt-injection defense, or native tool enforcement.


## Decision Lifecycle Ledger

- Valid hash chain: `true`
- Record count: `7`

## Evidence Boundary

MCP Proxy Runner v1 is a local reference proxy loop. It evaluates supplied MCP-style metadata, returns a proxy action, and records DLL evidence. It does not implement MCP transport, OAuth, enterprise identity, prompt-injection defense, sandboxing, native tool execution, or production policy distribution.
