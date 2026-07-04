# Scoped Workload Identity

## Purpose

SMERC separates the identity proposing an action from the identities issuing and consuming its authorization permit. This reduces the risk that an agent can treat its own proposal as permission to execute.

The reference API supports static, tenant-bound pilot principals with explicit endpoint scopes. An optional exchange can derive short-lived scope-narrowed sessions from those principals. This is separation of duties and bounded session issuance, not enterprise identity federation.

## Scope Model

| Scope | Authorized operations |
| --- | --- |
| `actions.evaluate` | Evaluate one action, an Action Language envelope, or a batch |
| `decisions.read` | List decisions, retrieve a decision, and read the review queue |
| `permits.issue` | Issue a permit for an eligible stored decision |
| `permits.consume` | Verify and consume a permit once |
| `reviews.read` | Read reviews for a decision |
| `reviews.write` | Record an immutable review |
| `metrics.read` | Read denominator-aware pilot metrics |
| `audit.read` | Read attributed permit and review security events |

Requests authenticate first and then fail with HTTP `403` and `insufficient_scope` when the principal lacks the operation's scope. Tenant assertions cannot override the principal's tenant.

## Configuration

`SMERC_API_PRINCIPALS` uses comma-separated entries in this form:

```text
tenant:principal:scope+scope=secret
```

Development-only example:

```powershell
$env:SMERC_API_PRINCIPALS="alpha:agent-proposer:actions.evaluate=alpha-proposer-local-secret-012345,alpha:permit-issuer:permits.issue=alpha-issuer-local-secret-01234567,alpha:deployment-executor:permits.consume=alpha-executor-local-secret-012345,alpha:security-reviewer:reviews.read+reviews.write=alpha-reviewer-local-secret-012345,alpha:security-auditor:decisions.read+metrics.read+audit.read=alpha-auditor-local-secret-012345"
```

Every deployed secret must contain at least 24 characters and be unique across all legacy and scoped credentials. Principal IDs, tenant IDs, and scopes are validated at startup. Scoped configuration cannot use the wildcard scope.

## Legacy Compatibility

`SMERC_API_KEYS=tenant=secret` remains supported. Each legacy key is represented as `legacy-{tenant}` with wildcard scope. This preserves existing pilots but does not provide separation of duties. New pilots should use scoped principals and leave `SMERC_API_KEYS` empty unless a compatibility path is required.

## Audit Binding

Every new decision and replay stores the authenticated `smerc.principal.v1` identity. Reviews store both:

- the authenticated workload principal, which is authoritative for access accountability
- the bounded reviewer alias supplied in the review body, which remains pilot metadata

Permit issuance, permit consumption, and review recording append `smerc.security-event.v1` records. Events include tenant, principal, event type, resource, bounded metadata, and timestamp. Permit tokens and credential secrets are never included.

`GET /v1/security-events` requires `audit.read` and remains tenant scoped.

## Short-Lived Sessions

When configured, `POST /v1/auth/token` accepts only a static bootstrap credential. It returns a signed session with explicit scopes, fixed issuer and audience, and a lifetime from 1 through 900 seconds. A session cannot call the exchange endpoint, gain scopes, change identity, or retain wildcard authority.

See `Short_Lived_Access_Operations.md` for configuration and limitations.

## Security Boundaries

- Bootstrap credentials are static bearer secrets, not OIDC, mTLS, SAML, SPIFFE, or cloud workload identity.
- Derived sessions expire, but the service has no remote revocation, refresh, introspection, exchange rate limiting, or managed secret store.
- Scope authorization protects API operations; it does not prove the external workload has the claimed real-world role.
- A stolen bootstrap credential can request sessions within its configured capabilities until operators rotate configuration and restart the pilot service.
- SQLite security events are append-only through the API, but they are not an immutable external audit ledger.
- Production deployment requires federated workload identity, short-lived credentials, managed rotation/revocation, centralized policy, monitoring, and export to an approved audit system.

## Recommended Pilot Roles

Use separate credentials for:

1. Agent or workflow proposer: `actions.evaluate`
2. Authorization service: `permits.issue`
3. Side-effecting executor: `permits.consume`
4. Security reviewer: `reviews.read+reviews.write`
5. Pilot auditor: `decisions.read+metrics.read+audit.read`

Do not give permit-issuance or permit-consumption credentials to the proposing agent.
