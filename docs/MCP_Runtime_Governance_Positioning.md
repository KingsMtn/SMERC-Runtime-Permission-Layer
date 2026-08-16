# MCP Runtime Governance Positioning

## Category

SMERC should be described as a pre-execution runtime governance layer for MCP-style tool calls, AI-agent actions, and automated workflows.

MCP helps agents connect to tools. SMERC evaluates whether a proposed tool call should execute now, whether it should be constrained, paused, escalated, or blocked, and what evidence should be preserved.

## Runtime Flow

```text
Agent
  -> MCP client or agent runner
  -> SMERC recoverability evaluation
  -> SPARTa route decision
  -> MCP server, tool adapter, approval queue, or block result
  -> Decision Lifecycle Ledger evidence
```

## Governance Question

Traditional permission checks usually ask:

> Is this identity or workflow allowed to call this tool?

SMERC asks an additional runtime question:

> Given evidence quality, anomaly pressure, reversibility, containment, rollback latency, and impact scope, should this specific call execute right now?

## How SMERC Differs From Core MCP Security

| Area | MCP-Oriented Control | SMERC Runtime Governance |
| --- | --- | --- |
| Tool availability | Which tools exist and how an agent can call them | Whether this proposed call is recoverable enough to execute |
| Identity | Which user, agent, or workload is authenticated | Whether the action posture should be ALLOW, THROTTLE, FREEZE, DENY, or ESCALATE |
| Authorization | Whether the actor has a declared permission | Whether risk, evidence, and reversibility justify execution now |
| Logging | What call happened | Why the decision was made, what controls were required, and how the outcome should be replayed |
| Prompt defense | Whether the request appears manipulated | Whether execution can be contained, reversed, or safely escalated even when the request is authorized |

## Current Reference Implementation

The current implementation is intentionally metadata-only. It does not execute MCP calls.

Implemented artifacts:

- `reference_engine/mcp_tool_governance.py`
- `reference_engine/mcp_proxy_runner.py`
- `reference_engine/mcp_transport_proxy.py`
- `examples/mcp/tool_call_delete_customer_records.json`
- `examples/mcp/tool_call_search_docs.json`
- `examples/mcp/transport_proxy_delete_customer_records.json`
- `examples/mcp/transport_proxy_search_docs.json`
- `docs/MCP_Tool_Governance.md`
- `docs/MCP_Proxy_Runner.md`
- `docs/MCP_Transport_Proxy.md`
- `tests/test_mcp_tool_governance.py`
- `tests/test_mcp_proxy_runner.py`
- `tests/test_mcp_transport_proxy.py`

The adapter maps tool-call metadata into:

- SMERC recoverability action
- SMERC posture
- SPARTa route state
- recommended MCP client/proxy result
- replayable evidence boundary

## Commercial Wedge

The near-term wedge is not a generic agent firewall claim. It is:

> Give security and platform teams a shadow-mode recoverability score before MCP-style tools, GitHub Actions, deployment workflows, and automation agents create side effects.

That is commercially useful because it can be tested without taking over a customer's identity system, tool registry, cloud account, or production enforcement path.

## Current Engineering Proof

The current proxy proof is `reference_engine/mcp_proxy_runner.py`. It:

1. receives a proposed tool call,
2. evaluates metadata through SMERC,
3. receives a SPARTa route,
4. returns `observe_and_forward_tool_call`, `forward_tool_call`, `forward_constrained_tool_call`, `hold_for_approval`, `pause_tool_call`, or `block_tool_call`,
5. records a Decision Lifecycle Ledger entry,
6. generates DLL Intelligence summary evidence.

The current transport sample is `reference_engine/mcp_transport_proxy.py`. It receives a local JSON-RPC-style `tools/call` envelope and returns either a forwarded result with SMERC replay evidence or a SMERC-blocked JSON-RPC error response.

## Evidence Boundary

SMERC's current MCP work is pilot-grade. It does not claim MCP compliance, Microsoft endorsement, marketplace approval, or production enforcement readiness.
