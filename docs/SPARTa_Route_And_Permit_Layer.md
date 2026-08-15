# SPARTa Route And Permit Layer

## Purpose

SPARTa is the routing and permit layer that follows a SMERC decision.

SMERC answers:

> Is the proposed action recoverable enough to execute now?

SPARTa answers:

> Given that posture, what route, controls, reviewer path, and execution permit should be applied?

This keeps the product boundary clear. SPARTa is not a replacement for IAM, OPA, Cedar, Microsoft Agent Governance Toolkit, ticketing, or workflow automation. It consumes a SMERC decision and translates it into operational control.

## Operating Model

```
Identity / IAM / OPA / Cedar
        |
        v
Authorized proposed action
        |
        v
SMERC recoverability decision
        |
        v
SPARTa route + permit report
        |
        v
Execution system / reviewer / workflow
        |
        v
DLL / audit / replay evidence
```

## Route Outcomes

| SMERC posture | SPARTa route | Permit status |
| --- | --- | --- |
| `ALLOW` | `release` | `issued` |
| `THROTTLE` | `constrained_execution` | `issued_with_constraints` |
| `FREEZE` | `pause_for_evidence` | `withheld_pending_evidence` |
| `DENY` | `block` | `withheld_blocked` |
| `ESCALATE` | `accountable_review` | `withheld_pending_approval` |

## What A Route Report Contains

- `route_id`
- `permit_id`
- SMERC posture
- SPARTa route
- permit status
- reviewer path
- required controls
- execution boundaries
- MCP tool-call context when present
- OPA/Cedar/IAM policy context when present
- OpenTelemetry-oriented trace context when present
- decision artifact hash
- optional HMAC route signature

## MCP Tool-Call Governance

MCP standardizes how agents discover and call tools. It does not, by itself, determine whether a tool call should execute under the current recoverability conditions.

SPARTa preserves MCP context such as:

- tool server
- tool name
- requested operation
- resource scope
- agent identity
- human sponsor
- delegated authority
- authority expiration

This allows a pilot customer to test SMERC/SPARTa at the tool-execution boundary without replacing the agent framework or policy engine.

## Policy Compatibility

SMERC/SPARTa should be positioned beside policy engines:

- IAM proves identity and grants base permissions.
- OPA/Rego or Cedar can determine whether the principal may perform the action.
- SMERC scores whether the action is recoverable enough to execute now.
- SPARTa converts the posture into route, permit, reviewer, and control instructions.

This avoids an unrealistic claim that SMERC replaces existing authorization systems.

## OpenTelemetry-Oriented Evidence

SPARTa route reports preserve trace-oriented fields:

- `trace_id`
- `span_id`
- `agent_invocation_id`
- `tool_execution_span`
- `smerc_replay_id`
- `sparta_route_id`

The current implementation does not claim full OpenTelemetry semantic-convention compliance. It provides compatible fields so a design partner can map SMERC decisions into existing observability pipelines.

## Reference Implementation

Run a SMERC decision:

```bash
python -m reference_engine.recoverability_engine examples/mcp_tool_call_action.json --pretty > mcp-decision.json
```

Generate a SPARTa route report:

```bash
python -m reference_engine.sparta_router examples/mcp_tool_call_action.json mcp-decision.json --pretty
```

Generate a signed route report:

```bash
python -m reference_engine.sparta_router examples/mcp_tool_call_action.json mcp-decision.json --signing-secret "replace-with-pilot-secret" --pretty
```

## Commercial Use

SPARTa is commercially useful when a buyer asks, "What happens after SMERC scores the action?"

The answer is concrete:

- low-risk actions receive a release permit;
- mixed-risk actions receive constrained execution;
- evidence-poor actions are paused;
- unrecoverable actions are blocked;
- high-impact uncertain actions are routed to an accountable reviewer.

The pilot objective is to measure whether those routes reduce irreversible exposure without blocking useful automation.
