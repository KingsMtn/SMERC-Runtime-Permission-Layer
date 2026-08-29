# Recovery Authority Gate

## Purpose

Recovery Authority Gate answers the question that appears after SMERC returns `FREEZE`, `ESCALATE`, or `DENY`:

> Who or what is allowed to unlock the pause, and what evidence is required before continuation?

This is the missing bridge between runtime permission and safe recovery. A pause is only useful if the system also knows how to reopen the path without letting the risky actor approve itself.

## Core Rule

The system that proposed or caused the risky action should not be able to unlock itself.

Unlock authority must be separate, verified, bounded, and recorded.

## Evaluation Inputs

Recovery Authority Gate evaluates four groups of facts:

| Input | Question |
| --- | --- |
| Paused decision | Is this actually a paused SMERC decision with replay ID and action hash? |
| Unlock actor | Is the actor different from the proposer, identity-verified, delegated, allowed, and conflict-free? |
| Unlock evidence | Has rollback, blast radius, missing evidence, fresh scan, evidence age, and override reason been handled? |
| Recovery path | Is continuation bound to replay, permit-gated, time-bounded, reviewer-backed, ledger-recorded, and monitored? |

## Output States

| State | Meaning |
| --- | --- |
| `UNLOCK` | Continue through a short-lived action-bound permit with ledger evidence and post-unlock monitoring. |
| `UNLOCK_CONSTRAINED` | Continue only after missing route controls are added. |
| `KEEP_PAUSED` | Do not reopen yet; evidence or route controls are incomplete. |
| `REQUALIFY` | The case is not a valid paused decision; re-run admission and SMERC scoring. |
| `DENY_UNLOCK` | The unlock actor or authority path is invalid, conflicted, or self-approving. |

## Work / Result / Impact

Work: evaluate whether a paused action can be safely reopened.

Result: a replayable unlock posture with reason codes and a required next step.

Impact: SMERC becomes more than a runtime stoplight. It becomes a governed recovery process where paused automation can restart only through verified authority, fresh evidence, a bounded route, an action-bound permit, and Decision Lifecycle Ledger evidence.

## Run

```bash
python -m reference_engine.recovery_authority_gate --pretty
```

Generated outputs:

- `reports/recovery_authority_gate_report.json`
- `reports/Recovery_Authority_Gate_Report.md`

## How It Fits

Recovery Authority Gate sits after:

1. runtime admission
2. SMERC recoverability scoring
3. SPARTa route selection
4. autonomy continuance checks

It sits before:

1. permit issuance
2. execution continuation
3. post-unlock monitoring
4. Decision Lifecycle Ledger outcome review

## Other Unanswered Process Issues For SMERC

The same industry gap suggests several next buildable issues:

- **Unlock authority:** who can reopen a paused action?
- **Evidence freshness:** how old can safety evidence be before it stops justifying continuation?
- **Self-approval prevention:** can the proposing agent, workflow, or team approve its own continuation?
- **Fallback complexity:** what happens when scanners, reviewers, ticket systems, policy engines, or rollback systems are unavailable?
- **Partial recovery:** can only part of the action continue while the risky part stays frozen?
- **Reviewer quorum:** when does one reviewer suffice, and when is dual approval required?
- **Post-unlock monitoring:** how long should the system watch after a paused action continues?
- **Learning safety:** should the decision history recommend policy changes without silently activating them?

These are not separate products yet. They are SMERC process layers that make runtime governance more complete.

## Boundary

Recovery Authority Gate is a pilot-grade reference model. It is not an IAM system, legal approval engine, production break-glass system, compliance attestation, or substitute for accountable human governance.
