# OpenSSF Issue #50 Response Draft

Thanks. This is useful feedback, especially the point about unavailable inputs. I agree that recoverability should not be bundled into one opaque score or used to rescue weak authority.

I am now thinking about the order as separate layers:

```text
static action / tool classification
-> scoped authority / typed contract / attestation / least privilege / expected object shape
-> runtime evidence and recoverability checks
-> posture
-> SPARTa route / controls
-> replayable lifecycle evidence
```

Your comment also exposed a concrete failure mode worth testing: unavailable evidence should not quietly become `ALLOW`.

I added explicit examples and tests for that:

- a low-impact action with a missing recoverability signal is capped from `ALLOW` to `THROTTLE`
- a production/external-side-effect action with missing rollback/evidence validity is capped from `ALLOW` to `FREEZE`
- the engine records `RECOVERABILITY_EVIDENCE_UNAVAILABLE` and signal-specific reason codes such as `ROLLBACK_LATENCY_UNAVAILABLE`

That keeps the rule explicit: missing recoverability evidence is uncertainty, not permission.

Relevant docs:

- https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/docs/Runtime_Evidence_Trust_Gate.md
- https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/docs/Ref_Gated_Runtime_Proof_Loop.md

Tests:

- `tests/test_recoverability_engine.py`

This is still pilot-grade and local. It does not claim production MCP enforcement, endpoint type safety, incident reduction, or compliance. The goal is narrower: make the boundary testable so missing rollback/recoverability evidence cannot be mistaken for permission to proceed.
