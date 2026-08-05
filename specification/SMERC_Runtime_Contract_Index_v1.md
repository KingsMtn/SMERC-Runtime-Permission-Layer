# SMERC Runtime Contract Index v1

## Purpose

`smerc.runtime-contract-index.v1` is the machine-readable map of the SMERC runtime system.

It answers:

> Which contract owns which part of the governance loop, and what artifact does it hand to the next layer?

This prevents SMERC from reading like unrelated schemas, reports, and integrations. It gives agents, adapters, reviewers, and future SDKs a canonical assembly map.

## System Loop

```text
agent/tool proposes action
-> action contract
-> runtime decision
-> executor fitness and policy context
-> SPARTa route and vocabulary
-> permit and control evidence when enforcement is active
-> PR/review/deployment artifact
-> Decision Lifecycle Ledger
-> DLL Intelligence
-> reviewed policy recommendation
```

## Contract Roles

| Layer | Contract | Role |
|---|---|---|
| Discovery | `smerc.beacon.v1` | Allows agents and reviewers to discover SMERC surfaces and boundaries. |
| Action request | `smerc.action.v1` | Describes the proposed action, risk signals, authority, and recovery context. |
| Runtime decision | `smerc.decision.v1` | Produces posture, scores, reason codes, controls, transition guidance, and replay. |
| Policy | `smerc.policy.v1` | Defines tenant thresholds, mode, evidence ceiling, and posture behavior. |
| Policy authoring | `smerc.spl.v0` | Pilot-friendly profile that compiles to the runtime policy contract. |
| Agent handshake | `smerc.agent_handshake.v1` | Connects discovery, agent declaration, executor fitness, action posture, and replay. |
| SPARTa route | `smerc.sparta-route.v1` | Converts posture and tool plan into executable, constrained, paused, blocked, or review-required route behavior. |
| SPARTa vocabulary | `smerc.sparta-vocabulary.v1` | Gives adapters and agents common route, control, evidence, and failure terms. |
| Permit | `smerc.permit.v1` | Grants short-lived, action-bound execution authority for eligible enforcement decisions. |
| Control evidence | `smerc.control-evidence.v1` | Records signed evidence that configured controls were applied or attempted. |
| Execution plan/report | `smerc.execution-plan.v1` and `smerc.execution-report.v1` | Describe how an authorized action will run and what happened. |
| Decision certificate | `smerc.decision-certificate.v1` | Produces a portable digest-bound summary of a verified decision lifecycle. |
| Lifecycle ledger | `smerc.decision-lifecycle-ledger.v1` | Preserves request, evidence, evaluation, human interaction, execution, outcome, and learning records. |
| Ledger intelligence | `smerc.dll-intelligence.v1` | Summarizes verified ledgers into near misses, overrides, recovery performance, drift, and review-gated policy recommendations. |

## Machine Contract

The canonical example is:

- `examples/runtime_contract_index.json`

The strict schema is:

- `schemas/smerc-runtime-contract-index-v1.schema.json`

## Interpretation Rules

1. Unknown contract versions do not imply compatibility.
2. Missing handoff artifacts make the runtime loop incomplete.
3. A restrictive posture cannot be relaxed by a downstream adapter.
4. DLL Intelligence may recommend policy changes, but it may not silently activate them.
5. Pilot evidence must remain labeled as pilot evidence until customer-context data supports stronger claims.

## Boundary

The runtime contract index is an assembly map. It is not production certification, compliance attestation, customer validation, or a guarantee that downstream tools enforced controls truthfully.
