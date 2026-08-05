# Microsoft-Style Security Replay Adapter

## Purpose

This adapter shows how SMERC can replay Microsoft Sentinel, Defender, Azure Activity, and advanced-hunting style security events and score the proposed automated response before execution.

The useful question is narrow:

> Given a Microsoft-style alert or incident and a proposed response action, should automation allow, throttle, freeze, deny, or escalate that response based on recoverability?

## What It Uses

The included dataset is synthetic, but shaped around public Microsoft security concepts:

- Microsoft Sentinel-style incidents and analytic rules
- Microsoft Defender-style alerts
- Azure Activity Log-style cloud change events
- advanced-hunting-style entity and event records

No private Microsoft customer telemetry is included.

## Command

```bash
python -m reference_engine.microsoft_security_replay \
  examples/microsoft_security_replay_events.json \
  --pretty
```

Outputs:

```text
reports/microsoft_security_replay_report.json
reports/Microsoft_Security_Replay_Report.md
```

## Input Shape

Each event records:

- Microsoft-style source, severity, category, and detection source
- entity counts such as devices, users, IPs, and subscriptions
- the current Microsoft-style workflow outcome, such as `AUTO_RESPONSE` or `ANALYST_REVIEW`
- the proposed response action
- SMERC recoverability signals for that response action

## Output Shape

The replay report includes:

- event source counts
- Microsoft-style workflow counts
- SMERC posture counts
- decision-difference rate
- auto-response actions restrained by SMERC
- review/escalation actions where SMERC found a bounded path
- average irreversible exposure by source
- per-event reason codes, controls, scores, and replay IDs

## Commercial Value

This gives Microsoft-oriented reviewers a concrete way to test the SMERC idea without handing over private logs:

1. start with public Microsoft-style event shapes,
2. map each event to a proposed response action,
3. run SMERC in shadow mode,
4. compare SMERC posture with the current workflow outcome,
5. decide whether recoverability scoring is worth testing on customer metadata.

## Evidence Boundary

This adapter does not claim Microsoft certification, Microsoft partnership, Sentinel validation, Defender validation, customer validation, threat detection, incident reduction, or replacement of Microsoft security tooling.

It is a pilot-grade replay path for evaluating whether recoverability scoring adds value before automated response actions execute.
