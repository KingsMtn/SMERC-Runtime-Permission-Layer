# Autonomy Continuance Framework

## Purpose

Autonomy Continuance answers:

> Does this AI system still have the right to continue acting from here?

It sits after SMERC action scoring, Earned Autonomy, and Autonomy Budgeting. Its role is to prevent a system from continuing simply because it once had permission.

## The Five Checks

### Authority Provenance

Authority Provenance asks whether the actor's authority is traceable and still valid.

It checks identity, delegation, policy binding, tool grant, required approval, and credential age.

If authority cannot be proven, the system should not continue.

### Intent Integrity

Intent Integrity asks whether the proposed action still matches the declared intent.

It checks whether scope, tool, data boundary, and operation class match what the actor said it was trying to do.

If intent diverges, the system should be requalified rather than allowed to keep acting under a misleading purpose.

### Consequence Horizon

Consequence Horizon asks how far the effects of the action can travel.

It considers external side effects, customer impact, financial settlement, rollback window, and downstream system count.

Long consequence horizons require more restraint than short reversible actions.

### Collective Autonomy

Collective Autonomy asks whether many agents or workflows are creating correlated pressure together.

One agent may appear safe in isolation while a group of agents creates shared-tool concentration, correlated objectives, or aggregate scope expansion.

### Right To Continue

Right To Continue combines the previous checks with Earned Autonomy and Autonomy Budgeting.

It returns:

- `CONTINUE`
- `CONTINUE_CONSTRAINED`
- `PAUSE`
- `REQUALIFY`

## Why This Matters

Runtime governance cannot stop at a single permission decision. AI systems may begin inside valid boundaries and drift outside them as tools, scope, timing, and multi-agent behavior change.

The right control is not just "was this allowed?" It is:

> Is it still authorized, still aligned, still bounded, still non-correlated, and still entitled to continue?

## Run

```bash
python -m reference_engine.autonomy_continuance --pretty
```

Generated outputs:

- `reports/autonomy_continuance_report.json`
- `reports/Autonomy_Continuance_Report.md`

## Boundary

This is a reference model for technical review and pilot design. It is not an IAM system, legal authority system, employee monitoring product, safety certification, or replacement for human accountability. Production use requires customer-owned policy mapping, calibrated thresholds, review labels, and legal/compliance review.
