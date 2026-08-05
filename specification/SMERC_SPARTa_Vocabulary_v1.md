# SMERC SPARTa Vocabulary v1

## Purpose

`smerc.sparta-vocabulary.v1` is the machine-readable control vocabulary for SPARTa adapters, agents, and review tools.

SMERC decides the posture. SPARTa translates that posture into tool behavior. The vocabulary gives machines a small set of verbs, route states, controls, evidence events, and failure reasons so they do not improvise different meanings for the same governance action.

This is not a programming language for arbitrary execution. It is a bounded control vocabulary for runtime governance.

## Core Rule

An adapter may only execute when the route state and control vocabulary allow execution.

If an adapter cannot interpret a required route state, control verb, evidence event, or failure reason, it must fail closed into review or blocking behavior.

## Lifecycle Verbs

| Verb | Meaning | Executable |
|---|---|---:|
| `DECLARE` | State adapter identity, supported actions, capabilities, controls, and evidence. | No |
| `PLAN` | Convert a requested action into a strict SPARTa tool plan. | No |
| `ROUTE` | Convert a SMERC posture and tool plan into a route report. | No |
| `PREPARE` | Reserve execution attempt, verify permit when required, and check native controls. | No |
| `EXECUTE` | Run the tool action under the route constraints. | Yes |
| `CONSTRAIN` | Apply reduced scope, dry run, checkpoint, rollback, approval, or rate controls. | Conditional |
| `HOLD` | Pause automation while preserving state and replay evidence. | No |
| `BLOCK` | Prevent automated execution. | No |
| `ESCALATE` | Route to accountable human or supervisory review. | No |
| `COLLECT_EVIDENCE` | Preserve non-secret evidence of controls, execution, review, or failure. | No |
| `APPEND_LEDGER` | Append route, execution, review, outcome, or learning evidence to DLL. | No |

## Route States

| Route State | Required Adapter Behavior |
|---|---|
| `EXECUTE` | Execute only after required preparation and evidence hooks are ready. |
| `CONSTRAINED_EXECUTE` | Execute only with required constraints applied and evidence captured. |
| `PAUSE` | Hold automation; preserve replay and state evidence. |
| `BLOCK` | Do not execute; preserve denial evidence. |
| `REVIEW_REQUIRED` | Do not execute until accountable review produces a valid response. |
| `BLOCKED_ESCALATION_UNAVAILABLE` | Do not execute because review was required but no valid review path exists. |

## Control Verbs

| Control Verb | Meaning |
|---|---|
| `LIMIT_SCOPE` | Reduce blast radius, quantity, accounts, files, transactions, or environment scope. |
| `PREVIEW_BEFORE_EXECUTION` | Run dry-run, plan, diff, simulation, or non-mutating preview first. |
| `CHECKPOINT_BEFORE_EXECUTION` | Capture restore point, state snapshot, artifact, or configuration baseline. |
| `REQUIRE_ROLLBACK_PLAN` | Require a declared rollback method before execution. |
| `REQUIRE_HUMAN_APPROVAL` | Require accountable human review before execution. |
| `PRESERVE_REPLAY` | Preserve decision replay ID and decision inputs used by SPARTa. |
| `REQUIRE_RECOVERY_PATH` | Require proof that recovery can be attempted within defined limits. |
| `RATE_LIMIT_EXECUTION` | Limit operation rate or transaction velocity. |
| `DELAY_SETTLEMENT` | Delay final external, financial, or irreversible commitment. |
| `REQUIRE_DUAL_CONTROL` | Require two accountable approvers or separation of duties. |
| `CANCEL_ON_SIGNAL_CHANGE` | Cancel or pause when material signals change after route issuance. |
| `REQUIRE_FRESH_EVIDENCE` | Require evidence freshness before action progression. |

## Evidence Events

| Event | Meaning |
|---|---|
| `ROUTE_ISSUED` | SPARTa route report was created. |
| `ROUTE_VERIFIED` | Route digest/signature or route-to-decision binding was verified. |
| `PERMIT_VERIFIED` | Action-bound permit was valid for this execution attempt. |
| `CONTROL_APPLIED` | Native control was applied or attempted. |
| `CONTROL_UNAVAILABLE` | Required native control was unavailable. |
| `EXECUTION_STARTED` | Tool execution began under a permitted route. |
| `EXECUTION_BLOCKED` | Execution was blocked before side effects. |
| `EXECUTION_PAUSED` | Execution was paused before final progression. |
| `EXECUTION_COMPLETED` | Execution completed under the declared route. |
| `EXECUTION_FAILED` | Execution failed and evidence was preserved. |
| `ROLLBACK_STARTED` | Rollback began. |
| `ROLLBACK_COMPLETED` | Rollback completed and evidence was preserved. |
| `ROLLBACK_FAILED` | Rollback failed or was incomplete. |
| `REVIEW_REQUESTED` | Accountable review was requested. |
| `REVIEW_COMPLETED` | Review response was received and bound to the route. |
| `LEDGER_APPENDED` | Decision Lifecycle Ledger was appended. |

## Failure Reasons

| Failure Reason | Required Behavior |
|---|---|
| `UNKNOWN_ADAPTER` | Block. |
| `UNSUPPORTED_ACTION` | Block. |
| `UNSUPPORTED_CAPABILITY` | Block. |
| `SCOPE_EXCEEDS_MAXIMUM` | Block or require review. |
| `CONTROL_UNSUPPORTED` | Require review or block. |
| `ROUTE_DIGEST_MISMATCH` | Block. |
| `PERMIT_MISSING` | Block enforcement execution. |
| `PERMIT_EXPIRED` | Block enforcement execution. |
| `PERMIT_ALREADY_USED` | Block enforcement execution. |
| `EVIDENCE_STALE` | Require fresh evidence or block. |
| `REVIEW_PATH_UNAVAILABLE` | Block escalation-unavailable. |
| `EXECUTION_RESULT_MISSING` | Treat execution evidence as incomplete; require review. |

## Machine-Readable Contract

A vocabulary document should use:

```json
{
  "version": "smerc.sparta-vocabulary.v1",
  "lifecycle_verbs": [],
  "route_states": [],
  "control_verbs": [],
  "evidence_events": [],
  "failure_reasons": [],
  "adapter_interpretation": {}
}
```

The strict schema is `schemas/smerc-sparta-vocabulary-v1.schema.json`.

An example vocabulary is `examples/sparta/sparta_vocabulary.json`.

## AI-Agent Interpretation Guidance

When an AI agent or coding assistant reads a SPARTa route, it should:

1. Treat route state as authoritative.
2. Never convert `PAUSE`, `BLOCK`, `REVIEW_REQUIRED`, or `BLOCKED_ESCALATION_UNAVAILABLE` into execution.
3. Map control verbs to native tool controls only when the adapter declares support.
4. Preserve unknown vocabulary as a failure condition, not as permission.
5. Return evidence events instead of silent success.
6. Append lifecycle evidence to DLL rather than silently updating policy.

## Boundary

This vocabulary improves machine interpretation. It does not prove that a downstream tool enforced a control truthfully, that a human reviewer was properly authenticated, or that production incident risk was reduced.
