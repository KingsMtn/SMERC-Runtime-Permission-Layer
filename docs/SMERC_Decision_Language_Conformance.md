# SMERC Decision Language Conformance

## Purpose

SMERC Decision Language conformance is a lightweight check for external frameworks that want to emit SMERC-compatible decision JSON.

The check answers one narrow question:

> Does this artifact speak the SMERC decision language clearly enough for another tool, reviewer, gateway, or runtime to understand the posture, route, controls, recoverability facts, evidence expectations, and replay boundary?

It does not require the external framework to use the SMERC reference engine.

## What It Checks

The conformance checker validates:

- `smerc.decision.v1` and `smerc.action.v1` version fields
- posture vocabulary: `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, `ESCALATE`
- posture-to-enforcement mapping
- posture-to-route mapping
- required route controls
- recoverability facts
- evidence expectations before execution, after execution, and during review
- postcondition expectations
- transition semantics, including `DENY` requiring a materially new request
- replay identity

## Why This Matters

The strategic goal is not only to prove SMERC can make decisions.

The larger ecosystem value is that other systems can emit decisions in the same shape. That makes SMERC useful as a shared action-governance vocabulary across AI agents, MCP gateways, cloud automation, CI/CD workflows, financial automation, and review systems.

## Run

```bash
python -m reference_engine.decision_language_conformance examples/decision_language/*.json --pretty
```

Write a report:

```bash
python -m reference_engine.decision_language_conformance examples/decision_language/*.json \
  --json-output reports/decision_language_conformance.json \
  --markdown-output reports/Decision_Language_Conformance_Report.md
```

## Evidence Boundary

This is contract-shape conformance only.

It does not prove:

- production enforcement
- customer-calibrated thresholds
- score correctness
- route-control execution
- postcondition evidence collection
- security certification
- government adoption

The useful claim is:

> This decision artifact is shaped so another system can understand and inspect the SMERC-compatible posture, route, controls, evidence expectations, and replay boundary.

