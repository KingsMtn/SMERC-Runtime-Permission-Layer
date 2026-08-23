# Autonomy Health Framework

## Purpose

Autonomy Health is the continuous operating layer that answers a different question from a single SMERC decision.

SMERC asks:

> Should this proposed action be allowed, throttled, frozen, denied, or escalated now?

Autonomy Health asks:

> How much independence should this AI system, agent, workflow, or tool family have over time?

This matters because one action can look acceptable while the broader agent is becoming less reliable, more aggressive, less recoverable, or harder to supervise.

## Autonomy Health Inputs

A practical Autonomy Health score should combine:

- Posture distribution: rising `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE` rates.
- Ref-gate failures: contract, attestation, least-privilege, or object-shape failures.
- Recoverability trend: declining reversible capacity and rising irreversible exposure.
- Evidence quality: missing, stale, self-attested, or conflicting evidence.
- Override behavior: high override rate, repeated overrides by the same team, or overrides that worsen outcomes.
- Reviewer agreement: low agreement between SMERC recommendations and qualified reviewers.
- Loop and velocity pressure: repeated tool calls, recursive attempts, and unusual action bursts.
- Scope expansion: attempts to exceed intended blast radius, tenant boundary, amount band, environment, or data class.
- Outcome feedback: incidents, near misses, rollback difficulty, customer impact, recovery time, and financial impact.

## Autonomy Health States

The reference operating model uses five states:

- `HEALTHY`: normal bounded autonomy remains appropriate.
- `WATCH`: autonomy continues, but evidence, velocity, or review patterns require monitoring.
- `DEGRADE`: reduce autonomy by adding constraints, smaller scope, or more review.
- `SUSPEND_AUTONOMY`: pause autonomous execution for this agent, tool family, or workflow.
- `REQUALIFY`: require owner review, policy update, model/tool validation, or new pilot evidence before autonomy is restored.

## Relationship To SMERC

SMERC is the action gate. Autonomy Health is the independence governor.

SMERC decisions feed Autonomy Health through:

- decision posture
- reason codes
- ref-gate checks
- SPARTa route state
- controls applied
- reviewer decisions
- execution outcome
- rollback outcome
- DLL learning record

Autonomy Health then feeds back into future SMERC evaluation by adjusting caps, required evidence, review requirements, domain profiles, and enforcement state.

## Example

A code agent may have several individual actions constrained rather than denied. Each action is recoverable enough with branch protection and dry-run controls. But if the same agent repeatedly exceeds scope, fails object-shape checks, triggers high anomaly pressure, and requires frequent reviewer correction, the agent's Autonomy Health should move from `WATCH` to `DEGRADE` or `SUSPEND_AUTONOMY`.

That is the product distinction:

- recoverability scoring governs the proposed action
- ref-gate checks prevent malformed or untrusted requests from being scored around
- Autonomy Health governs the ongoing permission level of the actor
- DLL preserves the evidence needed to justify those changes

## Commercial Use

Autonomy Health can become a CISO-visible dashboard for:

- which agents are safe enough to keep autonomous
- which workflows need more constraints
- which teams override too often
- which tool families create the most irreversible exposure
- which models or agents should be requalified before broader deployment

## Evidence Boundary

Autonomy Health is currently a framework and operating model. It should not be marketed as proven until pilot data shows that the score correlates with reviewer agreement, irreversible exposure reduction, lower false release rate, lower recovery cost, or fewer severe automation incidents.
