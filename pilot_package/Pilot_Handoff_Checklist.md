# SMERC Pilot Handoff Checklist

## Purpose

This checklist defines the handoff from external review to a bounded GitHub Actions shadow-mode pilot.

It is used after a prospect has reviewed:

- `docs/Reviewer_Quickstart.md`
- `docs/Customer_Action_Intake.md`
- `pilot_package/First_Pilot_Path.md`

The goal is to decide whether the prospect is ready to run SMERC in observe mode against one workflow.

## Handoff Decision

Proceed only when the answer is yes to all required items:

| Required Item | Yes/No | Evidence |
| --- | --- | --- |
| One workflow family is named. |  | Workflow name or repository scope. |
| One accountable security owner is named. |  | CISO delegate, security architect, or security engineering owner. |
| One accountable platform owner is named. |  | Platform, DevSecOps, or GitHub Actions owner. |
| The pilot starts in observe mode. |  | Existing workflow behavior is not blocked by SMERC. |
| The data boundary is metadata-only. |  | No secrets, credentials, raw customer records, source bodies, private prompts, or regulated payloads. |
| Reviewers can label decisions weekly. |  | Reviewer group and cadence are confirmed. |
| Stop conditions are accepted. |  | Security owner can pause or stop the pilot. |
| Success metrics are measurable. |  | Reviewer agreement, false release, false constraint, useful constraint, latency, and override metrics are available. |

## What The Customer Provides

Before kickoff, the customer provides:

- selected repository or workflow family
- workflow owner
- security owner
- reviewer list
- sample metadata-only actions
- current approval path
- current policy outcome where available
- artifact retention expectations
- security/data handling constraints
- stop conditions

The customer does not provide production secrets, credentials, private source bodies, raw customer records, regulated payloads, or confidential incident details unless a separate legal and security process approves it.

## What SMERC Provides

SMERC provides:

- action metadata template
- local scoring or API scoring path
- GitHub Actions observe-mode integration guidance
- posture, reason code, score, and control output
- replay identifiers
- optional tenant-scoped audit records
- weekly metrics format
- final pilot evidence report format
- go/no-go recommendation

SMERC does not provide production certification, compliance attestation, managed enterprise identity, customer legal approval, or guaranteed incident reduction.

## Week-Zero Gate

Do not start the pilot until these are complete:

1. Run reviewer quickstart.
2. Score customer action intake.
3. Confirm pilot fit is `moderate` or `strong`.
4. Confirm no fit-screen blockers.
5. Confirm metadata boundary in writing.
6. Confirm reviewer capacity.
7. Confirm the workflow can run in observe mode.
8. Confirm the customer accepts stop conditions.

## Observe-Mode Deliverables

During observe mode, collect:

- scored action count
- posture distribution
- reason-code distribution
- route-state distribution
- reviewer agreement
- override rate
- false release candidates
- false constraint candidates
- useful constraint examples
- latency observations
- unavailable evaluation count
- metadata quality notes

## Go/No-Go Outcomes

At the first decision point, choose one:

| Outcome | Meaning |
| --- | --- |
| Stop | SMERC did not add useful signal or integration cost is too high. |
| Narrow | A smaller workflow or better metadata boundary is needed. |
| Continue observe | More decision volume is needed before recommending controls. |
| Move to recommend | Show SMERC postures to reviewers during normal approval without blocking execution. |

Do not move to enforcement from this handoff checklist alone.

## Proof Standard

The handoff is successful only if a customer-side reviewer can say:

> I understand what SMERC will score, what evidence it will collect, what it will not collect, who reviews the output, and how we decide whether the pilot continues.

If that statement is not true, return to quickstart and action intake instead of starting a pilot.
