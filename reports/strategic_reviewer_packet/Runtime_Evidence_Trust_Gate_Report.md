# SMERC Runtime Evidence Trust Gate Report

- Generated: `2026-08-17T02:51:59+00:00`
- Scenarios evaluated: `3`
- Trust level counts: `{'HIGH': 1, 'LOW': 2}`
- Average trusted metadata score: `0.474`
- Admissible for runtime decision: `1`
- Decisions capped below ALLOW: `2`

## Scenario Results

| Action | Trust | Score | Max Posture | Missing Fields | High-Impact Self-Reported Fields |
|---|---:|---:|---:|---|---|
| trusted-github-actions-deploy | HIGH | 1.0 | ALLOW | None | None |
| mixed-mcp-tool-call | LOW | 0.423 | FREEZE | authority_basis | reversibility, rollback_method |
| agent-self-reported-database-cleanup | LOW | 0.0 | FREEZE | authority_basis, containment_strength, environment | actor, impact_scope, operation, resource, reversibility, rollback_method |

## Evidence Boundary

Synthetic examples demonstrate metadata-trust handling. Replace these records with customer-approved runtime metadata from proxies, OIDC claims, adapters, ticketing systems, or audit logs during a pilot.

