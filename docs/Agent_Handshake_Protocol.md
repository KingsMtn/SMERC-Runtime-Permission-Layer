# SMERC Agent Handshake Protocol

## Purpose

The SMERC Agent Handshake Protocol connects discovery to runtime governance.

The protocol answers:

> When an outside AI agent discovers SMERC, how does it declare itself, propose an action, receive a posture, and preserve a replayable governance record?

This is the bridge between the SMERC Beacon, Model and Agent Fitness, recoverability scoring, and replay.

## Flow

1. **Discover:** an agent reads `smerc-beacon.json` or `/.well-known/smerc.json`.
2. **Declare:** the agent submits identity, provider, capabilities, requested tool authority, and requested data access.
3. **Route:** SMERC evaluates whether the agent or another candidate executor is qualified for the task.
4. **Evaluate:** SMERC evaluates the proposed action through the recoverability engine.
5. **Respond:** SMERC returns a combined handshake posture, controls, reason codes, replay IDs, and replay record.

## Inputs

`smerc.agent_handshake.v1` accepts:

- beacon manifest
- agent declaration
- task route request for Model and Agent Fitness
- action request for recoverability scoring
- optional context

## Outputs

The response includes:

- `handshake_posture`
- `beacon_valid`
- `agent_issues`
- `recommended_executor`
- `executor_posture`
- `action_posture`
- reason codes
- controls
- fitness result
- action evaluation
- replay record

## Design Principle

The handshake does not trust a model because it can act. It requires the agent to discover the governance boundary, declare its capabilities and authority, and receive a posture before action.

If the agent declaration is inconsistent with the task, SMERC freezes the handshake even if the underlying executor candidate looks strong.

## Run

```bash
python -m reference_engine.agent_handshake examples/agent_handshake_request.json --pretty
python -m unittest tests.test_agent_handshake -v
```

## Boundary

The handshake is a pilot-grade reference protocol. It does not authenticate remote agents by itself, replace identity infrastructure, prove agent honesty, or provide production enforcement. In a deployment, it should be paired with scoped workload identity, signed permits, SPARTa routing, Decision Lifecycle Ledger records, and customer-specific policy.
