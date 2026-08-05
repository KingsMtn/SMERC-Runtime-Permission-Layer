# Real Public Incident Replay

This replay layer uses public incident reports as scenario seeds for SMERC.

It is designed to answer:

> When real public incident patterns are translated into proposed runtime actions, does SMERC add useful restraint compared with simple allow/deny assumptions?

## Inputs

Scenario file:

- `examples/real_public_incident_replay_scenarios.json`

Each scenario includes:

- source title
- publisher
- source URL
- incident date when known
- source facts
- replay question
- traditional allow/deny assumption
- analyst-assigned SMERC input signals

## Runner

```bash
python -m reference_engine.real_incident_replay \
  examples/real_public_incident_replay_scenarios.json \
  --json-output reports/real_public_incident_replay_report.json \
  --markdown-output reports/Real_Public_Incident_Replay_Report.md
```

## Current Sources

- GitHub availability report: May 2026
- GitHub Status incident history
- postmortems.app Keepthescore production database deletion postmortem
- postmortem.io public incident index entries for DNSSEC and control-plane API degradation patterns

## Evidence Boundary

The public incident facts are real public source facts.

The SMERC numeric inputs are analyst-assigned replay assumptions. They are not private telemetry, reconstructed internal system state, or proof that SMERC would have prevented the incident.

That source-fact versus analyst-assigned-signal boundary must stay visible in any external use of this report.

Use this replay for:

- sharper technical review
- scenario realism
- red-team questioning
- pilot hypothesis design

Do not use it as:

- customer validation
- production certification
- incident-prevention proof
- calibrated threshold evidence

## Current Result

The checked-in report currently evaluates six public incident-derived scenarios and produces:

- `THROTTLE` for multiple authorized-but-unstable operational actions
- `DENY` for a production database deletion with weak recoverability
- `ESCALATE` for a DNSSEC-style external resolution instability case

This is a stronger test than purely invented examples because it forces SMERC to face public operational failure patterns while keeping the limits honest.
