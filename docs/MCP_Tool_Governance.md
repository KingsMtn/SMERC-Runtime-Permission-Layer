# MCP Tool Governance

## Purpose

MCP helps agents discover and call tools. That creates a runtime governance question:

> Should this specific agent be allowed to execute this specific tool call right now?

SMERC fits as a pre-execution decision layer for MCP tool calls. It evaluates tool-call metadata before execution, scores recoverability and operational risk, and returns a replayable posture that SPARTa maps into a route.

## What SMERC Adds

SMERC does not replace MCP, OAuth, IAM, OPA, agent gateways, or prompt-injection defenses.

SMERC adds a recoverability-aware runtime question:

> If this MCP tool call goes wrong, can the organization contain, cancel, reverse, explain, and learn from it?

The MCP governance adapter maps one MCP tool-call request into:

- a SMERC recoverability action
- a SPARTa tool plan
- a SMERC posture
- a SPARTa route state
- a recommended MCP client/proxy result
- a replayable evidence record

## Command

```bash
python -m reference_engine.mcp_tool_governance \
  --request examples/mcp/tool_call_delete_customer_records.json \
  --pretty
```

Outputs:

```text
reports/mcp_tool_governance_report.json
reports/MCP_Tool_Governance_Report.md
```

## Example Outcomes

Destructive customer-record deletion:

- SMERC posture: `DENY`
- SPARTa route state: `BLOCK`
- recommended MCP result: `block_tool_call`

Read-only internal documentation search:

- SMERC posture: `ALLOW`
- SPARTa route state: `EXECUTE`
- recommended MCP result: `call_tool`

## Recommended MCP Result Values

| SMERC/SPARTa outcome | MCP client/proxy behavior |
| --- | --- |
| `EXECUTE` | `call_tool` |
| `CONSTRAINED_EXECUTE` | `call_tool_with_constraints` |
| `REVIEW_REQUIRED` | `require_approval_before_tool_call` |
| `PAUSE` | `pause_tool_call` |
| `BLOCK` | `block_tool_call` |

## Evidence Boundary

This adapter evaluates MCP tool-call metadata before execution. It does not implement MCP transport, OAuth, enterprise identity, sandboxing, prompt-injection defense, native tool enforcement, or production policy distribution.

The current value is proof of fit:

- SMERC can govern MCP-style tool-call requests before execution.
- SPARTa can translate SMERC posture into client/proxy behavior.
- DLL-style replay can preserve why a call was allowed, constrained, paused, escalated, or blocked.

Production use would still require integration with the actual MCP client, server, identity provider, tool registry, audit store, and enforcement point.

## MCP Proxy Runner

The next layer is now implemented as `reference_engine/mcp_proxy_runner.py`.

It wraps the MCP Tool Governance adapter in a local proxy loop with:

- `shadow` mode
- `enforce` mode
- explicit proxy response
- forwarding decision
- Decision Lifecycle Ledger record
- DLL Intelligence summary

Run:

```bash
python -m reference_engine.mcp_proxy_runner \
  --request examples/mcp/tool_call_delete_customer_records.json \
  --mode enforce \
  --pretty
```

See `docs/MCP_Proxy_Runner.md`.
