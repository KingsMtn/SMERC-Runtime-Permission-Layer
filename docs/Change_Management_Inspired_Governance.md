# Change-Management-Inspired Governance

SMERC should learn from change management without pretending to replace it.

Change-management systems ask whether a change has been requested, approved, scheduled, reviewed, and documented. SMERC asks a narrower runtime question:

> Is this specific automated action recoverable enough to execute now?

That difference matters for AI agents and automation because an approved ticket can still be dangerous at execution time. Evidence can be stale, rollback can be unproven, blast radius can widen, or anomaly pressure can rise after approval.

## What SMERC Borrows

SMERC borrows familiar operating discipline from change management:

- standard, normal, emergency, and rejected change labels
- pre-change evidence expectations
- approval and escalation discipline
- change-window awareness
- rollback-plan review
- post-change review
- auditability of who approved, overrode, executed, and learned from the outcome

SMERC converts those ideas into runtime signals that can be scored before the action executes.

## What SMERC Does Differently

Traditional change management often produces an approval status.

SMERC produces a runtime posture:

- `ALLOW`
- `THROTTLE`
- `FREEZE`
- `DENY`
- `ESCALATE`

The posture is based on recoverability, containment strength, rollback latency, evidence validity, anomaly pressure, impact scope, cancellation reliability, and authorization confidence.

## Why This Helps The GitHub Actions Pilot

The first practical lane is software delivery and infrastructure automation.

A GitHub Actions workflow can be approved by existing review processes but still deserve runtime restraint if:

- rollback evidence is weak
- the action touches production data
- the deployment has a wide blast radius
- the change is emergency-approved but poorly contained
- logs or evidence may be destroyed
- anomaly pressure changes after the ticket is approved

SMERC does not remove the change ticket. It creates a decision record around the moment of execution.

## Benchmark

Run the change-management-inspired benchmark:

```bash
python -m reference_engine.change_management_benchmark examples/change_management_governance_scenarios.json --pretty
```

Generated outputs:

- `reports/Change_Management_Governance_Benchmark.md`
- `reports/change_management_governance_benchmark.json`

The benchmark compares:

- traditional change-management outcomes: `APPROVE`, `APPROVE_WITH_CAB`, `EMERGENCY_APPROVE`, `REJECT`
- SMERC runtime postures: `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, `ESCALATE`

The key metric is the recoverability delta: scenarios where a traditional change label and SMERC runtime posture produce meaningfully different operating guidance.

## Evidence Boundary

This is a change-management-inspired benchmark only.

It is not ITIL certification, change-management software, ServiceNow/Jira replacement, CAB replacement, production approval, compliance attestation, customer validation, production certification, or incident-reduction proof.

## Commercial Position

For a CISO or platform leader, the useful claim is modest and testable:

> SMERC can sit beside existing change-management tools and score whether approved or rejected automated actions are recoverable enough to execute under current runtime conditions.

That gives SMERC a clearer lane. It is not another ticketing system. It is a runtime permission layer that uses recoverability to decide how automation should proceed.
