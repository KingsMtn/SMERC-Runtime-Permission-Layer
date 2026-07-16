# SMERC Human/AI Pilot Operating Model

## Purpose

This document defines who does what during a SMERC pilot. It prevents a common misunderstanding: the pilot is not a contest where the customer's AI decides whether SMERC works.

The correct model is human-supervised AI-action governance.

AI agents, bots, scripts, and workflows may propose actions. SMERC scores those proposed actions. Customer humans validate whether the scoring is useful, understandable, and operationally acceptable.

## Operating Principle

The first pilot should preserve human accountability.

SMERC can evaluate action metadata and produce a posture:

- `ALLOW`
- `THROTTLE`
- `FREEZE`
- `DENY`
- `ESCALATE`

But customer security, platform, and governance owners decide whether those postures are credible, noisy, useful, or unsafe for their environment.

## Role Split

| Participant | Primary responsibility | May automate? | Owns go/no-go? |
| --- | --- | --- | --- |
| AI agent or automation | Propose actions and emit metadata. | Yes. | No. |
| GitHub Actions or workflow system | Trigger jobs and pass action metadata to SMERC. | Yes. | No. |
| SMERC engine | Score recoverability, posture, reason codes, and controls. | Yes. | No. |
| Security reviewer | Label agreement, false release, false constraint, and useful constraint. | No for final labels. | Contributes. |
| Platform owner | Validate workflow fit, latency, and operational burden. | No for final pilot judgment. | Contributes. |
| CISO or delegate | Approve pilot scope, data boundary, and next mode. | No. | Yes. |
| SMERC project team | Provide setup guidance, reports, and interpretation support. | Partly. | No. |

## What The Customer's AI Can Do

During a pilot, customer AI or automation can:

- generate proposed actions
- produce structured action metadata
- call the SMERC GitHub Action or API
- attach SMERC reports to workflow artifacts
- route lower-risk actions through normal workflows
- propose reviewer notes
- collect telemetry for later human review

Customer AI should not be the final authority for:

- approving pilot scope
- approving data handling
- declaring SMERC correct
- labeling false release or false constraint
- moving from observe to recommend
- moving from recommend to enforce
- changing production policy without review

## What Humans Must Do

Humans must own:

- pilot approval
- selected workflow and environment
- data boundary
- reviewer definitions
- stop conditions
- interpretation of ambiguous decisions
- false release and false constraint labels
- override reasoning
- go/no-go decisions
- enforcement approval

This is especially important because a pilot is testing organizational judgment, not only software behavior.

## Evidence Flow

1. AI agent, bot, or workflow proposes an action.
2. Action metadata is generated within the approved data boundary.
3. SMERC evaluates the action and returns a posture, scores, reason codes, controls, and replay ID.
4. The workflow records a decision artifact.
5. Human reviewers compare SMERC output against current policy and operational judgment.
6. Reviewers label agreement, override, false release candidate, false constraint candidate, and useful constraint where applicable.
7. Weekly review summarizes posture distribution, reviewer agreement, overrides, latency, and evidence gaps.
8. CISO delegate and platform owner decide whether to stop, narrow, continue observe, move to recommend, or prepare limited enforcement.

## Pilot Modes By Human Involvement

| Mode | Automation role | Human role | Output |
| --- | --- | --- | --- |
| Observe | Generate actions, call SMERC, store reports. | Review samples and label outcomes. | Evidence on whether SMERC adds signal. |
| Recommend | Surface SMERC controls to reviewers. | Decide whether to follow or override guidance. | Evidence on decision support value. |
| Enforce-readiness | Test enforcement in non-production or tightly bounded scope. | Approve controls, rollback proof, stop conditions, and escalation path. | Evidence on operational safety. |
| Enforce | Block or constrain selected actions. | Must be approved by accountable customer owners. | Outside first-pilot default. |

## Human Review Labels

A useful pilot needs consistent labels:

- `agree`: reviewer agrees with SMERC posture
- `override_less_restrictive`: reviewer would allow more action than SMERC
- `override_more_restrictive`: reviewer would restrict more than SMERC
- `false_release_candidate`: SMERC allowed too much action
- `false_constraint_candidate`: SMERC constrained too much action
- `useful_constraint`: SMERC recommended a control the reviewer values
- `unclear_reasoning`: reviewer could not understand the decision

These labels should be entered by humans or approved by humans. AI-generated labels can be used as drafts only.

## Why This Matters To A CISO

A CISO is unlikely to buy SMERC because an AI says SMERC is good. A CISO is more likely to care if a controlled pilot shows:

- reviewers understand the posture decisions
- SMERC identifies hard-to-recover actions current controls treat as ordinary
- constraints reduce blast radius without creating excessive blocking
- false release and false constraint rates are measurable
- evidence can be replayed after the fact
- enforcement would be possible only after human-approved calibration

## Boundary Statement

SMERC can automate scoring. It should not automate accountability during a first pilot.

The pilot succeeds only if customer humans can use the evidence to make a defensible decision about whether SMERC should stop, narrow, continue, or expand.

