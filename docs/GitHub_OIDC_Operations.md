# GitHub Actions OIDC Operations

## Outcome

A trusted GitHub Actions job can call SMERC without storing `SMERC_API_KEY`. GitHub issues a short-lived signed identity token; SMERC verifies it against an exact local trust policy and returns a narrower workload-bound session for action evaluation.

## Server Configuration

Configure a distinct SMERC session-signing key:

```powershell
$env:SMERC_ACCESS_TOKEN_KEY="access-key-2026-01:replace-with-a-managed-32-byte-secret"
```

Set `SMERC_GITHUB_OIDC_TRUST` to a compact JSON array matching `schemas/smerc-github-oidc-trust-v1.schema.json`. The reviewable example is `examples/github_oidc/trust_policy.json`.

Required trust dimensions are:

- tenant
- repository name and immutable repository ID
- immutable repository-owner ID
- exact GitHub subject
- exact branch or tag refs
- exact workflow refs
- exact workflow commit SHAs
- allowed triggering events
- exact environment policy
- explicit SMERC scopes
- allowed GitHub-hosted or self-hosted runner class

An empty `environments` array means the OIDC token must not contain an environment claim. A non-empty array requires an exact allowed environment.

## Workflow Configuration

The job must request only the permissions it needs:

```yaml
permissions:
  contents: read
  id-token: write
```

Then select OIDC authentication:

```yaml
- uses: ./integrations/github_actions
  with:
    action-file: examples/recoverability_single_action.json
    source: remote
    api-url: ${{ vars.SMERC_API_URL }}
    auth-mode: github-oidc
    mode: observe
```

GitHub states that `id-token: write` permits requesting the OIDC token; it does not itself grant write access to repository resources. See the [GitHub OIDC reference](https://docs.github.com/en/actions/reference/security/oidc#workflow-permissions-for-the-requesting-the-oidc-token).

## Exchange Flow

1. The action requests audience `smerc-runtime-api` from the GitHub-provided token endpoint.
2. The action sends the resulting bearer token to `POST /v1/auth/github`.
3. SMERC verifies GitHub's signature, time claims, issuer, audience, and exact trust policy.
4. SMERC atomically registers the source token as exchanged.
5. SMERC returns `smerc.access-token.v2` with only `actions.evaluate` for the example policy.
6. The action calls `POST /v1/evaluate` with the SMERC session.
7. The decision stores verified workload context for audit and replay.

Neither GitHub's runtime request token nor its OIDC JWT is written to decision reports, workflow outputs, or security-event JSON.

## Rotation And Incident Handling

- Change `SMERC_ACCESS_TOKEN_KEY` and restart to invalidate outstanding SMERC sessions.
- Remove or narrow a trust policy to stop future exchanges.
- Disable the affected workflow or environment in GitHub when source trust is in question.
- Preserve `github_oidc.exchanged` events and decision records for investigation.
- Treat repository transfer, workflow change or rename, environment change, or subject customization as a trust-policy change requiring review. Every trusted workflow-code change requires an updated allowed `workflow_sha`.

## Reference Limits

- Replay prevention is atomic only for processes sharing the same SQLite database.
- JWKS is cached in process for five minutes; unknown key IDs trigger one refresh.
- There is no distributed cache, remote revocation, token introspection, or exchange rate limiter.
- A compromised trusted workflow can request a valid identity token within its configured claims.
- A compromised self-hosted runner can misuse credentials available to its job.
- GitHub identity does not establish that the proposed action data is truthful.
- The internal SMERC session remains an HMAC bearer token.

Use this implementation for controlled pilot deployment. Production expansion requires shared replay state, managed signing, observability, rate limits, and an organization-specific GitHub threat model.
