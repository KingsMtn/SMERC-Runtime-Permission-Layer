# SMERC Decision Language Implementer Quickstart

## Purpose

This quickstart shows how an external agent framework, MCP gateway, cloud workflow, CI/CD system, or review tool can emit a SMERC-compatible decision without adopting the full SMERC reference engine.

The goal is small:

> Produce one decision artifact that another system can read, route, review, and test for conformance.

## Input

Start with a plain action summary:

```json
{
  "framework": "example-agent-orchestrator",
  "action_id": "external-framework-cloud-change-001",
  "risk": {
    "irreversible_exposure": 0.58,
    "reversible_capacity": 0.71,
    "authorization_confidence": 0.82
  },
  "recoverability": {
    "rollback_ready": true,
    "blast_radius_bounded": true,
    "evidence_sufficient": false,
    "containment_strength": 0.76
  }
}
```

The full example is `examples/decision_language_inputs/external_framework_action.json`.

## Emit

Run:

```bash
python -m reference_engine.decision_language_emitter examples/decision_language_inputs/external_framework_action.json \
  --output reports/external_framework_smerc_decision.json \
  --pretty
```

The emitter returns `smerc.decision.v1` with:

- posture
- enforcement state
- route state
- required controls
- recoverability facts
- evidence expectations
- postcondition expectations
- transition requirements
- replay ID

## Validate

Run:

```bash
python -m reference_engine.decision_language_conformance reports/external_framework_smerc_decision.json --pretty
```

A passing result means the artifact speaks the portable SMERC decision language.

It does not mean the external system is certified, safe for production, or calibrated for a customer.

## Why This Helps Adoption

This gives an outside framework a low-friction path:

1. emit one SMERC-shaped decision
2. check conformance locally
3. map posture to its own route behavior
4. return postcondition evidence later

That is the cleanest ecosystem hook: other systems can adopt the vocabulary first, then integrate deeper runtime or postcondition evidence later.
