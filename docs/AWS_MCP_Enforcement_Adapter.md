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
- Every call must declare an incremental USD cost estimate. Unknown cost fails closed, positive cost requires
  trusted operator approval at adapter startup, and estimates above the `$2.00` pilot ceiling are blocked.
- Repeated approved calls accumulate an in-process estimate and stop before the session reaches `$5.00`.
- Successful results include the SMERC posture, route state, replay ID, reason codes, and required controls.
- Before execution, the adapter records a canonical SHA-256 binding for the exact AWS server, tool, and arguments.
- After a successful execution, the evidence envelope records a canonical result digest without treating that digest
  as independent proof that AWS native controls operated.

Run the reference stdio server:

```bash
python -m reference_engine.mcp_aws_enforcement_adapter
```

The command intentionally starts without an AWS executor and therefore cannot perform AWS operations. The
next integration step is a separately authenticated executor for the AWS managed MCP Server or a selected
AWS Labs MCP server. That executor must use scoped AWS identity and return CloudTrail/postcondition evidence;
it must not place AWS credentials in the MCP request.

The cost declaration is an admission control, not a substitute for AWS Budgets or billing reports. Estimates
must be derived before execution from current AWS pricing and the proposed resource shape. The pilot should
use a zero-spend AWS Budget as the independent account-level backstop.
The untrusted MCP request cannot approve its own spending. The operator may set `--approved-cost-usd` when
starting the adapter; it defaults to `0` and cannot be configured above `$2.00`.
The session counter is defense in depth, not an account-wide meter, and resets when the adapter restarts.

## Current boundary

This increment proves native MCP discovery, tool invocation, SMERC admission, exact target binding, and
fail-closed execution ownership. It does not yet implement AWS SigV4/OAuth identity brokering, managed AWS MCP
transport, CloudTrail correlation, independently attested AWS results, or production deployment in Bedrock AgentCore.
