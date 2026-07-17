# SPARTa Adapter Conformance

SPARTa adapter conformance is a static test layer for the adapter registry.

It answers a narrow technical question:

> Do the controls an adapter declares line up with the route states SPARTa actually produces?

The conformance harness probes every adapter across the five SMERC postures:

- `ALLOW`
- `THROTTLE`
- `FREEZE`
- `DENY`
- `ESCALATE`

For each posture it records the expected route state, actual route state, executable flag, applied controls, blocked controls, and capability gaps.

## Why This Matters

An adapter registry can look impressive while hiding weak execution paths.

For example:

- an adapter may claim deployment capability but lack scope limits
- a review adapter may support escalation but not constrained execution
- an observer may be useful for audit but should not be treated as an enforcement adapter
- an example adapter may be useful for demos but should stay marked as example-only

The conformance report turns those distinctions into explicit evidence.

## Command

```bash
python -m reference_engine.sparta_conformance examples/sparta/adapter_registry.json --pretty --json-output reports/sparta_conformance_report.json --markdown-output reports/SPARTa_Conformance_Report.md
```

## Evidence Boundary

This is a static adapter conformance report only. It verifies registry declarations against deterministic SPARTa route behavior.

It does not prove live ServiceNow, Jira, Slack, Teams, GitHub, cloud, financial, or Kubernetes enforcement. It does not prove production readiness, independent security review, or incident reduction.

The correct commercial use is pilot readiness:

1. show which adapter paths are coherent
2. show which paths remain mock or example-only
3. block overclaims before CISO review
4. define what live adapter evidence must be collected next
