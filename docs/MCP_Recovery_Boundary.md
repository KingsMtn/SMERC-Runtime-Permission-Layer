# MCP Recovery Boundary

`smerc.mcp-recovery-boundary.v1` is a pre-admission boundary for MCP tool calls. It replaces an unverified `supports_rollback: true` claim with the typed `smerc.recovery-capability.v1` evidence contract.

## Placement

The boundary runs before the existing MCP governance, identity, policy, SPARTa routing, permit, and transport-forwarding layers:

`tools/call -> recovery boundary -> Runtime Assurance governance -> SPARTa -> permit/enforcement -> MCP server`

Passing the boundary means only that the call is eligible for downstream governance. Every result sets `should_execute_tool: false` and `authority_effect: NONE`; this component never invokes an MCP tool.

## Behavior

- Mutating operations (`write`, `execute`, `deploy`, `delete`, and `payment`) require typed recovery capability evidence.
- Read-only calls may proceed without recovery capability evidence, but still require downstream governance.
- Verified evidence must match the MCP server, tool, environment, requested scope, mutation count, and acceptable rollback window.
- Stale, unverified, over-scope, or over-latency evidence produces a `FREEZE` hold.
- Missing, failed, malformed, expired, tampered, mismatched, or authority-claiming evidence produces `DENY`.

## Why This Matters

MCP tool descriptions are supplied metadata, not enforcement truth. A server saying it supports rollback does not establish what is restored, who can trigger recovery, how long rollback takes, or whether the mechanism was tested. This boundary makes those claims structured and fail-closed before a mutating call reaches execution routing.

## Boundary

This is a reference contract, not native MCP protocol conformance, OAuth, authentication, sandboxing, or proof that an external recovery mechanism works. Production use still needs trusted adapter identity, action-to-resource binding, independent evidence, replay protection, and observed recovery outcomes.
