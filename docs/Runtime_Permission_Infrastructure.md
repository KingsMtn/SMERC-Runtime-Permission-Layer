# SMERC Runtime Permission Infrastructure

## Positioning

SMERC is runtime permission infrastructure for AI agents and high-stakes automated systems.

It sits between model outputs, tools, data, and real-world actions. Before an AI agent sends an email, edits code, deletes data, moves money, calls an API, or triggers a workflow, SMERC evaluates the proposed action and returns a replayable posture.

## Five Replayable Postures

- `ALLOW`: proceed because the action is low risk, expected, authorized, and replayable.
- `THROTTLE`: proceed with constraints such as preview, rate limit, smaller scope, delay, stronger logging, or recovery proof.
- `FREEZE`: pause because the system lacks enough confidence, context, or evidence to proceed safely.
- `DENY`: reject because the action is too harmful, unauthorized, irreversible, or outside policy.
- `ESCALATE`: route to human or higher-trust review because the action may be legitimate but consequence is high.

## Why This Is Not Just An AI Firewall

AI firewalls, prompt filters, and guardrails are useful, but they often focus on model input, model output, jailbreaks, prompt injection, or content safety.

SMERC's sharper lane is the execution boundary:

> The moment an AI agent is about to do something consequential.

At that boundary, the key question is not only whether text is safe. The key question is whether the proposed action should be allowed, slowed, paused, rejected, or escalated based on confidence, harm, consent, reversibility, and side effects.

## First Product Wedge

The first wedge is AI agent governance at the tool/action boundary.

Initial action categories:

- send external message
- edit code
- run command
- deploy software
- change cloud configuration
- access sensitive data
- delete data
- trigger financial workflow
- call internal API

## Minimal Input Shape

```json
{
  "action_id": "SEND_EMAIL_TO_CUSTOMER",
  "description": "Agent sends a customer-facing email.",
  "tool": "gmail.send",
  "actor": "sales_agent",
  "confidence": 0.72,
  "harm": 0.42,
  "consent": 0.66,
  "reversibility": 0.38,
  "external_effect": true,
  "sensitive_data": false
}
```

## Minimal Output Shape

```json
{
  "posture": "THROTTLE",
  "risk_score": 0.463,
  "confidence_score": 0.622,
  "constraints": [
    "limit_scope",
    "preview_before_execution",
    "log_replay",
    "rate_limit_external_effect",
    "require_recovery_path"
  ],
  "reason_codes": [
    "EXTERNAL_SIDE_EFFECT",
    "LOW_REVERSIBILITY"
  ],
  "replay_id": "replay_SEND_EMAIL_TO_CUSTOMER_..."
}
```

## YC One-Liner

SMERC is permission infrastructure for AI agents, controlling when automated systems should allow, throttle, freeze, deny, or escalate actions.

## Founder Video Direction

SMERC: Signal Gate can be used as a visual metaphor, not as the company itself. The prototype shows signals arriving with urgency, confidence, harm, and consent, then being routed through permission gates.

The real product is the runtime governance layer that sits between agent plans and side-effecting tools.

## Implementation Status

The repository now includes:

- Python runtime permission engine: `reference_engine/agent_permission_layer.py`
- Example action requests: `examples/agent_permission_actions.json`
- Unit tests: `tests/test_agent_permission_layer.py`
- Existing reversibility-weighted authorization and public demos

