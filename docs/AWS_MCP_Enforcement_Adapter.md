# AWS MCP Enforcement Adapter

`reference_engine.mcp_aws_enforcement_adapter` is the first native MCP-facing execution boundary for SMERC.
It exposes one MCP tool, `smerc_guarded_aws_call`, and evaluates the supplied AWS action before a trusted
AWS MCP executor can run it.

## Enforcement contract

- The AWS server and tool names must exactly match the SMERC governance request.
- Agent identity is required.
- Only a clean `ALLOW` decision can reach the configured executor.
- `THROTTLE`, `FREEZE`, `DENY`, and `ESCALATE` return MCP tool errors and do not execute.
- Missing executor configuration, malformed input, evaluation failure, and executor failure all fail closed.
- Successful results include the SMERC posture, route state, replay ID, reason codes, and required controls.

Run the reference stdio server:

```bash
python -m reference_engine.mcp_aws_enforcement_adapter
```

The command intentionally starts without an AWS executor and therefore cannot perform AWS operations. The
next integration step is a separately authenticated executor for the AWS managed MCP Server or a selected
AWS Labs MCP server. That executor must use scoped AWS identity and return CloudTrail/postcondition evidence;
it must not place AWS credentials in the MCP request.

## Current boundary

This increment proves native MCP discovery, tool invocation, SMERC admission, exact target binding, and
fail-closed execution ownership. It does not yet implement AWS SigV4/OAuth identity brokering, managed AWS MCP
transport, CloudTrail correlation, or production deployment in Bedrock AgentCore.
