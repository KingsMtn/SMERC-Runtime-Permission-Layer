# MCP Proxy Runner

The MCP Proxy Runner is a local reference loop that wraps the existing MCP Tool Governance adapter.

It is not a full MCP transport implementation. It does not claim MCP protocol compliance, OAuth integration, enterprise identity enforcement, sandboxing, prompt-injection defense, native tool execution, or production policy distribution.

It does prove a concrete runtime path:

```text
MCP-style tool request
  -> SMERC MCP Tool Governance
  -> SMERC recoverability decision
  -> SPARTa route
  -> proxy response
  -> Decision Lifecycle Ledger
  -> DLL Intelligence
```

## Modes

| Mode | Behavior |
| --- | --- |
| `shadow` | Always forwards the tool call, but records what SMERC would have recommended. |
| `enforce` | Applies the proxy action derived from SMERC and SPARTa. |

## Proxy Actions

| Proxy action | Meaning |
| --- | --- |
| `observe_and_forward_tool_call` | Shadow mode only; forward while recording evidence. |
| `forward_tool_call` | Forward a tool call that SMERC/SPARTa allowed. |
| `forward_constrained_tool_call` | Forward only with the listed controls and reduced scope. |
| `hold_for_approval` | Do not forward until accountable approval exists. |
| `pause_tool_call` | Pause because evidence or conditions are unstable. |
| `block_tool_call` | Block and require a safer new request. |

## Run

Shadow mode:

```bash
python -m reference_engine.mcp_proxy_runner \
  --request examples/mcp/tool_call_delete_customer_records.json \
  --mode shadow \
  --pretty
```

Enforce mode:

```bash
python -m reference_engine.mcp_proxy_runner \
  --request examples/mcp/tool_call_delete_customer_records.json \
  --mode enforce \
  --json-output reports/mcp_proxy_runner_report.json \
  --markdown-output reports/MCP_Proxy_Runner_Report.md \
  --pretty
```

## Example

For `examples/mcp/tool_call_delete_customer_records.json`, enforce mode returns:

- SMERC posture: `DENY`
- SPARTa route: `BLOCK`
- proxy action: `block_tool_call`
- should forward tool call: `false`
- DLL record count: `7`

For `examples/mcp/tool_call_search_docs.json`, enforce mode returns:

- SMERC posture: `ALLOW`
- SPARTa route: `EXECUTE`
- proxy action: `forward_tool_call`
- should forward tool call: `true`

## What It Adds Beyond MCP Tool Governance

`reference_engine/mcp_tool_governance.py` answers:

> What should an MCP client or proxy do with this proposed tool call?

`reference_engine/mcp_proxy_runner.py` adds:

- shadow/enforce mode behavior
- explicit proxy response shape
- forwarding decision
- forwarding plan
- proxy instructions
- Decision Lifecycle Ledger
- DLL Intelligence summary

## Evidence Boundary

This is pilot-grade local software. Production use would still require integration with the actual MCP client, MCP server, identity provider, tool registry, audit store, policy administration, human review queue, and enforcement point.
