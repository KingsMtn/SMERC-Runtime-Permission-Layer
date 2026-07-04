# Short-Lived Access Operations

## Configuration

Set one pilot access-token signing key:

```powershell
$env:SMERC_ACCESS_TOKEN_KEY="access-key-2026-01:local-access-token-secret-0123456789012345"
```

The format is `key-id:secret`; the secret requires at least 32 characters. This example is development-only. Store real values in an approved secret manager. The server rejects reuse of an API principal, permit-signing, or control-evidence signing secret for access tokens.

## Exchange

Authenticate with the principal's static credential:

```bash
curl -X POST http://127.0.0.1:8788/v1/auth/token \
  -H "Authorization: Bearer platform-proposer-local-secret-012345" \
  -H "Content-Type: application/json" \
  --data '{"scopes":["actions.evaluate"],"ttl_seconds":300}'
```

The response contains `access_token`, `token_type`, `expires_in`, `expires_at`, and the non-secret session claims. Keep the token in process memory and send it as the Bearer credential for ordinary API calls.

Omit `scopes` to receive every explicit scope available to the bootstrap principal. Prefer requesting only the scopes needed for one workload stage.

## Rotation

The reference server accepts one signing key at a time. Changing `SMERC_ACCESS_TOKEN_KEY` and restarting immediately invalidates outstanding sessions. Coordinate rotation with workload retries and do not rely on this behavior as a production revocation system.

## Audit

Each exchange records tenant, principal, session ID, scopes, key ID, issuance, expiry, and legacy origin. The access token and bootstrap secret are never included. Decisions made with a session preserve its ID and expiry for correlation.

## Operating Limits

- Maximum session lifetime: 900 seconds
- No refresh tokens
- No session-to-session exchange
- No wildcard session scopes
- No remote revocation or introspection endpoint
- No built-in exchange rate limiting
- No OIDC, cloud identity, SSO, or hardware-backed key integration

Use this layer to reduce static-secret exposure in a controlled pilot, not as a substitute for enterprise identity federation.
