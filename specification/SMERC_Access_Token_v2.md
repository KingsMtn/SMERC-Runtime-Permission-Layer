# SMERC Short-Lived Access Token v2

## Purpose

`smerc.access-token.v2` is the current short-lived SMERC bearer-session contract. It preserves v1 tenant, principal, scope, audience, and lifetime controls and adds an authenticated `workload_context` claim.

Static exchange sets `workload_context` to `null`. A verified GitHub OIDC exchange binds the signed GitHub workload context into the SMERC session and every decision made with it.

## Compatibility

New sessions use v2. The verifier accepts structurally valid v1 sessions until their normal expiry. V1 does not carry workload context and must not be represented as federated identity.

## Claims

V2 contains all v1 fields plus `workload_context`:

- `null` for static bootstrap exchange
- a strict `github_actions_oidc` object for GitHub federation

The GitHub object binds subject, repository and owner IDs, workflow and commit identities, triggering ref, run and attempt, actor, event, runner class, token ID, and optional environment or reusable-workflow ref.

Unknown workload fields, missing required fields, unknown providers, empty values, invalid scopes, wildcard authority, altered signatures, wrong audience, and expired sessions are rejected.

## Lifetime And Authority

- Session lifetime is 1 through 900 seconds.
- A federated session cannot outlive its source GitHub OIDC identity.
- Session scopes cannot exceed the bootstrap principal or OIDC trust policy.
- Sessions cannot call token-exchange endpoints.
- HMAC key reuse across API credentials, permits, control evidence, and access sessions is rejected at startup where configured values are visible.

## Security Boundary

V2 carries verified context; it does not independently verify the truth of a proposed action or the safety of a workflow. The bearer token must remain in process memory and must not be logged, committed, or uploaded as an artifact. Production expansion requires managed signing, rotation, revocation, monitoring, and shared replay infrastructure.
