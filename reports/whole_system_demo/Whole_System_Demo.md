# SMERC Whole-System Demo

Generated: `2026-09-14T11:16:49+00:00`
Version: `smerc.whole-system-demo.v1`
Status: `whole_system_complete`

## One-Line Summary

SMERC takes one proposed high-impact action from identity/context through recoverability scoring, posture, route controls, separate recovery authority, bounded execution, postcondition evidence, and a valid decision lifecycle ledger.

## System Flow

```text
Identity / Context
        -> Recoverability Engine
        -> Decision Posture
        -> SPARTa Route Controls
        -> Recovery Authority Gate
        -> Bounded Continuation
        -> Executor / Gateway
        -> Postcondition Evidence
        -> Decision Lifecycle Ledger
```

## Stage Results

| Stage | Role | Result |
| --- | --- | --- |
| Identity / Context | Validates actor, session, typed contract, attestation, least privilege, object shape, and required evidence before scoring. | `ADMIT` |
| Recoverability Engine | Scores whether the proposed action is reversible, bounded, observable, and safe enough to proceed. | `FREEZE` |
| Decision Posture | Converts recoverability judgment into the shared SMERC decision language. | `FREEZE` |
| SPARTa Route Controls | Translates posture into execution routing, required controls, and whether the action can execute. | `PAUSE` |
| Recovery Authority Gate | Requires separate authority and fresh recovery evidence before a paused action can continue. | `UNLOCK` |
| Bounded Continuation | Re-scores the narrowed continuation action and routes it through constrained execution. | `CONSTRAINED_EXECUTE` |
| Executor / Gateway | Executes only the permitted bounded route, using a short-lived action-bound permit. | `succeeded` |
| Postcondition Evidence | Records whether the required controls and execution result can be checked after the route. | `succeeded` |
| Decision Lifecycle Ledger | Preserves a replayable chain of request, evidence, evaluation, human interaction, execution, outcome, and learning records. | `valid` |

## Summary

- overall_status: `COMPLETE`
- initial_posture: `FREEZE`
- initial_route: `PAUSE`
- unlock_state: `UNLOCK`
- continuation_posture: `THROTTLE`
- continuation_route: `CONSTRAINED_EXECUTE`
- execution_status: `succeeded`
- ledger_valid: `True`

## Linked Proofs

- complete_lifecycle_proof: `docs/Complete_Lifecycle_Proof.md`
- aws_decision_api_surface: `docs/AWS_Decision_API_Surface.md`
- trace_evidence_adapter: `docs/TRACE_Evidence_Adapter.md`
- postcondition_evidence: `docs/Postcondition_Evidence.md`
- customer_metadata_request: `docs/Customer_Owned_Metadata_Request.md`

## Evidence Boundary

This is a deterministic, metadata-only whole-system demo. It does not execute production commands, connect to AWS, GitHub, MCP servers, Linux Foundation projects, TRACE runtimes, or customer systems, prove production safety, certify compliance, prove customer demand, or prove incident reduction.

## Work / Result / Impact

- Work: show SMERC as one coordinated runtime safety system, not a pile of separate artifacts.
- Result: one action moves from identity/context to recoverability, posture, route controls, bounded continuation, execution evidence, and ledger verification.
- Impact: reviewers can understand the whole system before inspecting the deeper AWS, TRACE-style, postcondition, or customer-metadata proof paths.
