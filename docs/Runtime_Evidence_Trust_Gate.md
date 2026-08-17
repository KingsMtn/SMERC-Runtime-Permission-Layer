# Runtime Evidence Trust Gate

## Purpose

SMERC should not treat an AI agent's self-description as trusted evidence for high-impact actions.

If an agent says:

> This delete operation is reversible and low risk.

SMERC still needs to ask:

- Who observed the action metadata?
- Was the evidence authenticated?
- Was it signed or hash-bound?
- Was it collected by a proxy, adapter, OIDC claim, ticketing system, audit event, or human-review record?
- Which fields came only from the proposing agent?
- Are high-impact fields such as actor, authority, environment, resource, reversibility, or rollback method independently observed?

The Runtime Evidence Trust Gate scores whether supplied metadata is reliable enough for SMERC to use as runtime governance evidence.

## Command

```bash
python -m reference_engine.runtime_evidence_trust --pretty
```

Outputs:

```text
reports/runtime_evidence_trust_report.json
reports/Runtime_Evidence_Trust_Gate_Report.md
```

## Inputs

The default examples live in:

```text
examples/runtime_evidence_trust_examples.json
```

Each scenario declares:

- evidence sources
- assertion types
- authentication and signature status
- evidence freshness
- required fields
- observed fields and their sources
- fields supplied by the proposing agent

Trusted assertion types include:

- GitHub OIDC claims
- MCP proxy observations
- deployment adapter receipts
- human-review records
- ticketing-system records
- cloud audit events
- signed runtime attestations

## Outputs

The gate returns:

- `trust_level`: `HIGH`, `MEDIUM`, `LOW`, or `UNTRUSTED`
- `trusted_metadata_score`
- field coverage score
- authentication score
- freshness score
- independence score
- agent-supplied metadata penalty
- missing required fields
- high-impact self-reported fields
- reason codes
- required controls
- maximum recommended posture

## How It Changes SMERC

This gate answers one of the most important critiques of the public build:

> SMERC is useful only if the action metadata comes from a trustworthy runtime boundary, not from the proposing agent's self-description.

The gate makes that rule operational.

If metadata is fresh, signed, authenticated, and independently observed, SMERC can use it for normal shadow-mode decision evidence.

If metadata is mixed, SMERC can still produce a constrained recommendation but should cap the posture below unrestricted `ALLOW`.

If high-impact fields are self-reported by the agent, SMERC should freeze, deny, or require replacement evidence from a proxy, adapter, OIDC claim, audit event, ticket, or reviewer.

## Evidence Boundary

This is a pilot-grade metadata trust screen. It does not prove action safety, production readiness, compliance, incident reduction, or customer validation.

Its job is narrower and commercially important:

> prevent SMERC from becoming dependent on untrusted agent-supplied context.

