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

For the AWS managed MCP Server, `ManagedAWSMCPProxyExecutor` constructs a locked-down stdio command for a
locally installed and reviewed `mcp-proxy-for-aws` executable. It only accepts AWS managed HTTPS `/mcp`
endpoints, validates the resource Region metadata, and inherits `shell=False` execution. SMERC does not
download the proxy, accept a floating package version, or handle AWS credentials. Operators should pin and
review the proxy package and provide short-lived SigV4 credentials through the standard AWS credential chain.
An interactive Codex OAuth session is not assumed to transfer to the proxy subprocess.

After installing a pinned, reviewed proxy build, select the constrained route explicitly (options must precede
the proxy command because the remaining arguments are passed through verbatim):

```bash
python -m reference_engine.mcp_aws_enforcement_adapter \
  --aws-resource-region us-east-2 \
  --managed-aws-proxy-command uvx mcp-proxy-for-aws-cli@PINNED_VERSION
```

The cost declaration is an admission control, not a substitute for AWS Budgets or billing reports. Estimates
must be derived before execution from current AWS pricing and the proposed resource shape. The pilot should
use a zero-spend AWS Budget as the independent account-level backstop.
The untrusted MCP request cannot approve its own spending. The operator may set `--approved-cost-usd` when
starting the adapter; it defaults to `0` and cannot be configured above `$2.00`.
The session counter is defense in depth, not an account-wide meter, and resets when the adapter restarts.

## Current boundary

This increment proves native MCP discovery, tool invocation, SMERC admission, exact target binding, fail-closed
execution ownership, and a constrained command route to AWS's managed MCP proxy. It does not yet provision or
broker AWS credentials, correlate CloudTrail events, independently attest AWS results, or deploy in Bedrock AgentCore.
