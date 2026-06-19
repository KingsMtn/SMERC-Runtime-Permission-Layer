# Layer Model

## Layer 1: Source Systems

LLMs, AI agents, prediction models, rule engines, fraud systems, workflow systems, safety layers, and operational software produce proposed actions or risk observations.

## Layer 2: Signal Normalization

Domain context is mapped into SMERC's common signal vocabulary. This layer should be transparent and tested because signal quality directly affects governance quality.

## Layer 3: Macro Authorization

The SMERC engine evaluates stress, confidence, reason codes, and decision state. This layer is intentionally conservative and interpretable.

## Layer 4: Enforcement

The decision is translated into concrete system controls:

- `ALLOW`: execute.
- `THROTTLE`: reduce scope, speed, amount, permission, route, or autonomy.
- `DENY`: block.
- `FREEZE`: halt, isolate, and require explicit release.

## Layer 5: Oversight

Audit logs, human review, compliance reporting, threshold governance, and incident review close the loop.
