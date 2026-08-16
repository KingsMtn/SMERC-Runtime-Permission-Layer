# MCP Transport Proxy Sample

The MCP Transport Proxy sample shows the next runtime step after MCP Proxy Runner.

It accepts a local JSON-RPC-style `tools/call` envelope, evaluates the attached MCP-style governance request through SMERC, and returns either:

- a forwarded JSON-RPC result with SMERC replay evidence attached, or
- a JSON-RPC error response that explains why SMERC did not forward the tool call.

It is not a production MCP gateway and does not claim MCP compliance.

## Runtime Flow

```text
JSON-RPC-style tools/call request
  -> MCP Transport Proxy sample
  -> MCP Proxy Runner
  -> MCP Tool Governance
  -> SMERC recoverability decision
  -> SPARTa route
  -> JSON-RPC result or error
  -> Decision Lifecycle Ledger evidence
```

## Why This Matters

The prior MCP adapter proved that SMERC can score MCP-style tool-call metadata.

The MCP Proxy Runner proved that SMERC can produce shadow/enforce proxy actions.

This sample proves the reviewer-facing transport pattern: an agent asks to call a tool, SMERC decides whether that call should be forwarded, and the caller receives a machine-readable response.

## Run

Blocked destructive action:

```bash
python -m reference_engine.mcp_transport_proxy \
  --envelope examples/mcp/transport_proxy_delete_customer_records.json \
  --pretty
```

Forwarded read-only action:

```bash
python -m reference_engine.mcp_transport_proxy \
  --envelope examples/mcp/transport_proxy_search_docs.json \
  --pretty
```

Write report files:

```bash
python -m reference_engine.mcp_transport_proxy \
  --envelope examples/mcp/transport_proxy_delete_customer_records.json \
  --json-output reports/mcp_transport_proxy_report.json \
  --markdown-output reports/MCP_Transport_Proxy_Report.md \
  --pretty
```

## Example Outcomes

`transport_proxy_delete_customer_records.json` returns a JSON-RPC error with:

- proxy action: `block_tool_call`
- SMERC posture: `DENY`
- SPARTa route: `BLOCK`
- replay ID and reason codes

`transport_proxy_search_docs.json` returns a JSON-RPC result with:

- proxy action: `forward_tool_call`
- SMERC posture: `ALLOW`
- SPARTa route: `EXECUTE`
- replay evidence attached under `result.smerc_proxy`

## Evidence Boundary

This is pilot-grade local software. Production use would still require real MCP client/server integration, authentication, authorization, tenant policy distribution, tool registry integration, network transport, sandboxing, observability, and operational runbooks.
