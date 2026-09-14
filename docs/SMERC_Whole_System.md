# SMERC Whole System

## Purpose

SMERC is not one filter and not one API endpoint.

It functions as a coordinated runtime safety system for consequential automated action.

The short version:

```text
SMERC is the recoverability brain.
SPARTa is the route and control translator.
Adapters bring outside evidence in and carry route evidence out.
The Decision Lifecycle Ledger makes the system reviewable.
```

## Whole-System Flow

```text
Identity / Context
        -> Recoverability Engine
        -> Decision Posture
        -> SPARTa Route Controls
        -> Executor / Gateway
        -> Postcondition Evidence
        -> Decision Lifecycle Ledger
        -> Reviewer / Auditor / Policy Improvement
```

For paused or frozen actions, the flow adds:

```text
Recovery Authority Gate
        -> Bounded Continuation
        -> Action-Bound Permit
```

## System Roles

### Identity / Context

Checks who or what is acting, what scope is available, whether the session is valid, whether typed contracts and evidence are present, and whether the proposed action is admissible for scoring.

### Recoverability Engine

Scores whether the action is reversible, bounded, observable, and safe enough to execute now.

It looks at signals such as:

- reversibility
- rollback latency
- containment strength
- impact scope
- evidence validity
- anomaly pressure
- cancel reliability
- authorization confidence
- external side effects
- sensitive data pressure

### Decision Posture

Returns the shared SMERC decision language:

- `ALLOW`
- `THROTTLE`
- `FREEZE`
- `DENY`
- `ESCALATE`

### SPARTa Route Controls

Translates posture into execution behavior:

- execute
- constrain scope
- preview first
- checkpoint first
- require rollback plan
- preserve replay
- hold for review
- block execution

### Executor / Gateway

The actual platform still executes or holds the action.

That platform may be GitHub Actions, an AWS-style Lambda or API gateway, an MCP gateway, a cloud automation runner, or another runtime.

SMERC does not need to own the executor. It governs the recoverability decision before side effects happen.

### Postcondition Evidence

Checks whether the required route controls actually happened.

Examples:

- AWS-style postcondition evidence
- TRACE-style runtime evidence metadata
- GitHub Actions reports
- MCP gateway observations
- customer-owned metadata
- signed adapter evidence

### Decision Lifecycle Ledger

Records request, evidence, evaluation, human interaction, execution, outcome, and learning recommendation events so the decision can be reviewed later.

## Runnable Demo

Run:

```bash
python -m reference_engine.whole_system_demo --pretty
```

This writes:

- `reports/whole_system_demo/Whole_System_Demo.md`
- `reports/whole_system_demo/whole_system_demo.json`

The demo uses the complete lifecycle case:

- a broad production deployment is proposed
- runtime admission passes
- SMERC returns `FREEZE`
- SPARTa routes to `PAUSE`
- a separate recovery authority unlocks after fresh rollback evidence
- the narrowed canary action is rescored
- SPARTa routes to constrained execution
- an action-bound permit is issued and verified
- execution is simulated
- the Decision Lifecycle Ledger validates

## Related Proofs

- `docs/Complete_Lifecycle_Proof.md`
- `docs/AWS_Decision_API_Surface.md`
- `docs/TRACE_Evidence_Adapter.md`
- `docs/Postcondition_Evidence.md`
- `docs/Customer_Owned_Metadata_Request.md`
- `docs/AWS_Reviewer_Bundle.md`

## Evidence Boundary

This is a local, metadata-only explanation and demo path. It does not execute production commands, connect to AWS, GitHub, MCP servers, TRACE runtimes, Linux Foundation projects, or customer systems, prove production safety, certify compliance, prove customer demand, or prove incident reduction.

## Work / Result / Impact

Work:

Make SMERC understandable as one coordinated runtime safety system.

Result:

Reviewers can see how identity/context, recoverability scoring, posture, SPARTa routing, execution boundaries, postcondition evidence, and the Decision Lifecycle Ledger fit together.

Impact:

The repo becomes easier to inspect because the many proof artifacts now have one system map and one runnable whole-system demo.
