# AWS OAuth Handshake Retry Boundary

SMERC's direct AWS MCP OAuth executor applies bounded retry only before an AWS tool operation begins.

- HTTP 429 during `initialize` or `notifications/initialized` may be retried.
- `Retry-After` is honored up to the configured delay ceiling.
- Handshake attempts are capped at five and default to three.
- HTTP 429, timeout, or transport failure during `tools/call` is never retried.
- OAuth tokens and upstream response bodies are not included in raised errors.

This boundary avoids duplicate cloud effects when the outcome of an operation is ambiguous. It does not change AWS service quotas, guarantee that AWS will accept a later handshake, or establish that an AWS operation succeeded.
