# SMERC Short-Lived Access Token v1

## Purpose

`smerc.access-token.v1` lets a configured static tenant principal obtain a short-lived bearer session for ordinary SMERC API calls. The session carries an explicit subset of the bootstrap principal's scopes and preserves tenant and principal attribution.

This reduces repeated use of long-lived credentials. It is not OIDC, OAuth, SAML, SPIFFE, managed identity, or proof of the external workload that presented the bootstrap secret.

## Trust Boundary

Only `POST /v1/auth/token` accepts a static bootstrap credential for exchange. A short-lived token cannot call that endpoint to mint another token. The exchange cannot add scopes, change tenant or principal, or place wildcard authority in a session.

The reference implementation signs tokens with one pilot HMAC key configured through `SMERC_ACCESS_TOKEN_KEY`. That key must be distinct from API principal, permit-signing, and control-evidence signing secrets; startup rejects known reuse. A compromised bootstrap credential can obtain sessions within its authority. A compromised signing key can mint arbitrary sessions.

## Compact Format

```text
base64url(header).base64url(claims).base64url(HMAC-SHA256(header.claims))
```

The header fixes:

- `alg`: `HS256`
- `typ`: `SMERC-ACCESS`
- `kid`: configured signing-key identifier

The claims bind:

- version and unique session ID
- fixed issuer and audience
- tenant and principal IDs
- sorted, unique, explicit API scopes
- whether the bootstrap principal came from legacy all-scope configuration
- issuance, activation, and expiry times

## Lifetime

The default lifetime is 300 seconds. A request may select 1 through 900 seconds. Activation equals issuance and expiry is exclusive. There is no refresh token.

## Scope Narrowing

Scoped principals may request only their configured scopes. Legacy wildcard principals are converted to the current explicit scope set; `*` never appears in an access token. Omitting `scopes` selects all explicit scopes available to the bootstrap principal.

## Authentication

Protected endpoints first test configured static credentials and then, when enabled, verify short-lived tokens. Verification requires exact header and claim fields, signature, issuer, audience, canonical scopes, activation, and expiry.

Decisions and replays record:

- `credential_type: short_lived_access_token`
- session ID and expiry
- tenant, principal, explicit scopes, and legacy origin

Token issuance appends `access_token.issued` without storing the bearer token.

## Security Boundaries

- HMAC is shared-key authentication, not public nonrepudiation.
- Tokens are bearer credentials and must be protected in transit and memory.
- There is no token revocation list; expiry bounds exposure.
- There is no rate limiter on the reference exchange endpoint.
- Static bootstrap secrets still require rotation and controlled storage.
- The exchange does not validate cloud, CI, or human identity assertions.
- Production requires federated workload identity, managed signing, rotation/revocation, monitoring, rate limits, and incident response.

## Versioning

The contract version is `smerc.access-token.v1`. Changes to claims, signature rules, issuer/audience, lifetime, or scope semantics require a new version.
