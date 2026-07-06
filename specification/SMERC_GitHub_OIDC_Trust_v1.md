# SMERC GitHub Actions OIDC Trust v1

## Purpose

`smerc.github-oidc.v1` verifies the identity context of a GitHub Actions job before SMERC issues a short-lived authorization session. It replaces a stored `SMERC_API_KEY` for the action-evaluation path; it does not replace SMERC policy, action scoring, permits, or native GitHub protections.

The implementation follows GitHub's OIDC issuer, signed JWT, custom claims, and `id-token: write` model documented in the [GitHub OpenID Connect reference](https://docs.github.com/en/actions/reference/security/oidc).

## Trust Decision

SMERC accepts an exchange only when all of the following are true:

1. The compact JWT uses `RS256`, has type `JWT`, and references exactly one GitHub JWKS key.
2. The RSA signature verifies against keys fetched from GitHub's fixed JWKS endpoint.
3. Issuer is `https://token.actions.githubusercontent.com` and audience is `smerc-runtime-api`.
4. Issuance, activation, expiry, and maximum 900-second source lifetime are valid.
5. Repository name, immutable repository ID, immutable owner ID, exact subject, ref, workflow ref, workflow commit SHA, event, environment presence/value, and runner environment match exactly one configured policy.
6. Requested SMERC scopes are a subset of that policy.
7. The GitHub token ID and token digest have not already been exchanged in the audit store.

Any failed condition prevents session issuance.

## Bound Context

The resulting `smerc.access-token.v2` carries:

- GitHub subject, repository name, repository ID, and owner ID
- workflow ref and workflow commit SHA
- triggering ref and action commit SHA
- run ID and attempt
- actor ID and event name
- runner environment
- optional deployment environment and reusable-workflow ref
- source token ID for correlation inside the signed session

Every decision and replay stores this context in `authenticated_principal.workload_context`.

## Session Rules

- The session receives only explicit policy scopes and may be further narrowed by the exchange request.
- Wildcard scopes are forbidden.
- The session expires no later than both 900 seconds and the source GitHub OIDC token.
- The GitHub token can be exchanged once in the configured SQLite audit store.
- The resulting SMERC session cannot call either static or GitHub exchange endpoints.
- Existing `smerc.access-token.v1` tokens remain verifiable until their normal expiry; new issuance uses v2.

## Security Boundary

GitHub OIDC proves that GitHub signed the presented claims. It does not prove that workflow code is safe, the initiating actor intended the result, a self-hosted runner is uncompromised, branch protections are sufficient, or an action deserves execution. Exact trust policy and SMERC authorization remain separate decisions.

The reference implementation uses a single-process JWKS cache, SQLite replay state, and an HMAC-signed SMERC session. Multi-instance enforcement requires shared transactional replay storage, managed signing, monitoring, revocation procedures, and deployment-specific threat review.

## Versioning

The trust contract version is `smerc.github-oidc.v1`. Changes to issuer, audience, signature algorithm, required claims, matching rules, or replay semantics require a new version.
