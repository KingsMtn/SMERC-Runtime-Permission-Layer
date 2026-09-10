# SMERC Decision Language

## Purpose

SMERC Decision Language is a machine-readable contract for AI action governance.

It lets an agent, tool gateway, runtime, cloud workflow, reviewer, or audit system exchange the same basic decision:

> Should this action proceed, slow down, pause, escalate, or stop, and what evidence is required before or after execution?

The contract is designed to be useful even when a system does not adopt the full SMERC reference engine.

## Standardization Boundary

SMERC Decision Language is the portable vocabulary. The SMERC engine is one implementation.

An external framework can implement the decision language by emitting:

- one posture: `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE`
- one enforcement state: `release`, `constrain`, `pause`, `block`, or `review`
- route controls that explain what must happen before execution
- recoverability facts that explain rollback, blast radius, evidence, and containment
- evidence expectations that explain what must be preserved
- a replay identifier that lets reviewers compare the decision later

This makes SMERC a reusable decision contract rather than only a local runtime.

## Posture Vocabulary

| Posture | Meaning | Typical route |
| --- | --- | --- |
| `ALLOW` | Proceed because authority, recoverability, evidence, and containment are sufficient. | `EXECUTE` |
| `THROTTLE` | Proceed only with constraints such as scope limits, previews, checkpoints, or rollback controls. | `CONSTRAINED_EXECUTE` |
| `FREEZE` | Pause until evidence, rollback, or recovery state is restored. | `PAUSE` |
| `DENY` | Do not execute. A materially new request is required. | `BLOCK` |
| `ESCALATE` | Require accountable human or governance review before constrained execution. | `REVIEW_REQUIRED` |

## Contract Files

- Schema: `schemas/smerc-decision-language-v1.schema.json`
- Beacon schema: `schemas/smerc-beacon-v1.schema.json`
- Beacon example: `examples/smerc_beacon.json`
- Posture examples: `examples/decision_language/`
- Runtime action contract: `specification/SMERC_Action_Language_v1.md`

## Minimal Decision Shape

```json
{
  "language_version": "smerc.decision.v1",
  "action_language_version": "smerc.action.v1",
  "action_hash": "0000000000000000000000000000000000000000000000000000000000000000",
  "action_id": "example-action",
  "posture": "THROTTLE",
  "enforcement_state": "constrain",
  "route_state": "CONSTRAINED_EXECUTE",
  "required_controls": ["limit_scope", "preview_before_execution", "require_rollback_plan"],
  "recoverability": {
    "rollback_ready": true,
    "blast_radius_bounded": true,
    "evidence_sufficient": false,
    "containment_strength": 0.74
  },
  "scores": {
    "irreversible_exposure": 0.51,
    "reversible_capacity": 0.73,
    "authorization_confidence": 0.81
  },
  "reasons": [{"code": "EXTERNAL_SIDE_EFFECT", "title": "Action has an external side effect"}],
  "structured_controls": [{"code": "limit_scope", "title": "Limit action scope"}],
  "evidence_expectation": {
    "pre_execution": ["preview_before_execution", "checkpoint_before_execution"],
    "postcondition": ["record_execution_report", "preserve_replay"],
    "review": []
  },
  "postcondition_expectation": {
    "must_preserve_replay": true,
    "must_record_execution": true,
    "must_report_missing_controls": true
  },
  "transition": {
    "mode": "conditional",
    "eligible_target_posture": "ALLOW",
    "requires_new_request": false,
    "conditions": []
  },
  "replay_id": "example-replay",
  "replay": {}
}
```

## Ecosystem Use

The useful adoption path is intentionally small:

1. A framework publishes a SMERC beacon or points to one.
2. A tool call, agent action, cloud change, or workflow emits a SMERC-compatible decision.
3. An executor maps the posture to route behavior.
4. A reviewer or postcondition process checks whether the required controls actually happened.

That lets MCP gateways, cloud automation, CI/CD systems, financial automation, or internal governance tools reuse the same posture vocabulary without claiming SMERC certification.

## Non-Claims

This contract is not a government standard, certification, cloud-provider endorsement, production safety proof, or legal compliance guarantee.

The stronger claim is narrower and more credible:

> SMERC Decision Language is a candidate machine-readable contract for recoverability-aware AI action governance.

## Validation

Run:

```bash
python -m unittest tests.test_decision_language_contract -v
python -m unittest tests.test_action_language tests.test_beacon -v
```
