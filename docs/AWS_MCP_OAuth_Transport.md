# AWS MCP OAuth Transport

`AWSOAuthMCPExecutor` is the direct Streamable HTTP route from an admitted
SMERC action to the AWS managed MCP endpoint. It is intentionally separate
from admission, cost policy, and evidence generation.

## Boundary

The executor:

- accepts a token from an injected provider only after SMERC admits the call;
- connects only to the reviewed HTTPS AWS MCP endpoint;
- binds initialization, MCP session, tool name, arguments, and response ID;
- retries once with a refreshed token after HTTP 401;
- limits response size and rejects malformed, mismatched, or failed results;
- never returns or records access or refresh tokens.

The token provider owns OAuth 2.1 authorization, PKCE, refresh-token rotation,
secure operating-system storage, introspection, and revocation. This split
prevents credentials from entering SMERC decision inputs or evidence bundles.
AWS access tokens last up to one hour, and interactive refresh tokens are
rotated and single-use. A provider must therefore perform atomic refresh-token
replacement and fail closed if storage or rotation fails.

`OAuthTokenHelperProvider` defines the host integration contract. It launches a
fixed argv without a shell and sends this JSON on standard input:

```json
{"version":"smerc.oauth-token-helper.v1","operation":"get_access_token","resource":"https://aws-mcp.us-east-1.api.aws/mcp","force_refresh":false}
```

The helper returns exactly a JSON object containing `token_type: "Bearer"` and
`access_token`. Its implementation should read the host's protected credential
store and atomically rotate refresh tokens. SMERC bounds helper time and output,
redacts helper output on failure, and keeps the token in process memory only.

## Threat-Control Overlay

Threat taxonomies belong around the adapter, not inside its protocol state
machine. The minimum review overlay is:

| Threat | Required control |
| --- | --- |
| Token disclosure | OS-backed secret storage; redact headers and exceptions |
| Redirect or endpoint substitution | Exact HTTPS host and path allowlist; no redirects |
| Request substitution | Bind admitted tool and canonical arguments to the receipt |
| Response substitution | Require matching JSON-RPC ID and valid MCP result |
| Replay | Short-lived access token, rotated refresh token, bounded MCP session |
| Privilege expansion | Existing IAM least privilege and AWS MCP condition keys |
| Authentication loss | One controlled refresh, then fail closed |
| Oversized or malformed response | Byte limit, UTF-8 and JSON-RPC validation |

SPARTA can be used as an optional external threat-model crosswalk when SMERC is
deployed in a space-system context. It is not a runtime dependency for general
AWS workloads. For general deployments, the controls above can be crosswalked
to the organization's chosen threat and assurance frameworks.

## Remaining Live-Proof Step

Provide a reviewed token provider backed by the host credential store, then
pass `AWSOAuthMCPExecutor(provider)` to `AWSMCPEnforcementAdapter`. The existing
enforced live-proof runner must create a success artifact only after the direct
executor returns a matching successful result.

AWS references:

- <https://docs.aws.amazon.com/signin/latest/userguide/aws-mcp-server.html>
- <https://docs.aws.amazon.com/agent-toolkit/latest/userguide/security_iam_service-with-iam.html>
