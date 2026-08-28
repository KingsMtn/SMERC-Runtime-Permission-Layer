# SMERC MCP Proxy Runner Report

Generated: `2026-08-28T01:21:30+00:00`

## Proxy Decision

- Mode: `enforce`
- Agent identity required: `true`
- MCP request: `MCP_SEARCH_INTERNAL_DOCS_001`
- Agent: `developer_assistant_agent`
- Server: `engineering_docs_mcp`
- Tool: `search_internal_docs`
- Proxy action: `forward_tool_call`
- Should forward tool call: `true`
- SMERC posture: `ALLOW`
- SPARTa route: `EXECUTE`
- Identity gate: `PASS`
- Replay ID: `replay_MCP_MCP_SEARCH_INTERNAL_DOCS_001_1787880090001_fa9f37fec260`

## Proxy Instructions

- Forward the tool call and preserve the replay and route evidence.

## Governance Report

# SMERC MCP Tool Governance Report

Generated: `2026-08-28T01:21:30+00:00`

## Summary

- MCP request: `MCP_SEARCH_INTERNAL_DOCS_001`
- Agent: `developer_assistant_agent`
- MCP server: `engineering_docs_mcp`
- Tool: `search_internal_docs`
- SMERC posture: `ALLOW`
- SPARTa route state: `EXECUTE`
- Executable: `true`
- Recommended MCP result: `call_tool`

## Reason Codes

- `RECOVERABILITY_ACCEPTABLE`

## Agent Identity Gate

- Status: `PASS`
- Score: `0.8`
- Reason codes: `['AGENT_IDENTITY_VERIFIED']`

## Controls

- `execute`
- `record_execution_report`

## Plain English

SMERC evaluated MCP tool `search_internal_docs` for agent `developer_assistant_agent` and returned ALLOW. SPARTa mapped that posture to `EXECUTE`, so an MCP client or proxy should use `call_tool` rather than blindly executing the tool call.

## Evidence Boundary

This adapter evaluates MCP tool-call metadata before execution. It does not implement MCP transport, OAuth, enterprise identity, sandboxing, prompt-injection defense, or native tool enforcement.


## Decision Lifecycle Ledger

- Valid hash chain: `true`
- Record count: `7`

## Evidence Boundary

MCP Proxy Runner v1 is a local reference proxy loop. It evaluates supplied MCP-style metadata, returns a proxy action, and records DLL evidence. It does not implement MCP transport, OAuth, enterprise identity, prompt-injection defense, sandboxing, native tool execution, or production policy distribution.
