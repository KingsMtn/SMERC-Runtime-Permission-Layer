# SMERC MCP Transport Proxy Report

Generated: `2026-08-16T04:26:53+00:00`

## Transport Decision

- Proxy request: `MCP_TRANSPORT_DELETE_CUSTOMER_RECORDS_001`
- Mode: `enforce`
- JSON-RPC request ID: `tool-call-001`
- MCP method: `tools/call`
- Tool: `delete_customer_records`
- Proxy action: `block_tool_call`
- Forwarded: `false`
- SMERC posture: `DENY`
- SPARTa route: `BLOCK`

## JSON-RPC Response Shape

```json
{
  "error": {
    "code": -32070,
    "data": {
      "posture": "DENY",
      "proxy_action": "block_tool_call",
      "proxy_instructions": [
        "Block the tool call.",
        "Preserve the replay and explain the denial.",
        "Require a materially safer new request before execution."
      ],
      "reason_codes": [
        "IRREVERSIBLE_EXPOSURE_HIGH",
        "RECOVERY_CAPACITY_LOW",
        "ROLLBACK_LATENCY_HIGH",
        "CANCEL_RELIABILITY_WEAK",
        "CONTAINMENT_WEAK",
        "IMPACT_SCOPE_WIDE",
        "EXTERNAL_SIDE_EFFECT",
        "SENSITIVE_DATA"
      ],
      "replay_id": "replay_MCP_MCP_DELETE_CUSTOMER_RECORDS_001_1786854413231_3125f63bc09c",
      "route_state": "BLOCK"
    },
    "message": "SMERC proxy did not forward the MCP tool call."
  },
  "id": "tool-call-001",
  "jsonrpc": "2.0"
}
```

## Summary

SMERC returned DENY and the transport proxy produced JSON-RPC error -32070 instead of forwarding the tool call.

## Evidence Boundary

MCP Transport Proxy v1 is a local JSON-RPC-style reference sample. It demonstrates how SMERC can sit between an MCP-style tools/call request and execution. It does not implement network transport, MCP session negotiation, OAuth, identity brokering, sandboxing, native tool execution, or production MCP compliance.
