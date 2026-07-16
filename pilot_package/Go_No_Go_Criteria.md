# SMERC Pilot Go/No-Go Criteria

## Purpose

This document defines evidence thresholds for deciding whether a pilot should start, continue, expand, or stop.

## Start Pilot: Go Criteria

Proceed if:

- one workflow has clear ownership
- action metadata can be generated safely
- customer approves metadata-only data boundary
- reviewers are available
- existing approvals remain authoritative
- success metrics are agreed before launch
- stop conditions are agreed before launch
- pilot can run in observe mode first

Do not start if:

- customer expects immediate production blocking
- customer cannot provide reviewers
- pilot requires raw secrets or regulated payloads
- workflow owner is unknown
- success cannot be measured
- customer treats pilot output as compliance certification

## Day 30: Continue Criteria

Continue if:

- action metadata is reliable
- decisions are understandable
- reviewer agreement can be measured
- no serious data boundary violation occurred
- integration overhead is acceptable
- customer can identify at least some useful recommendations

Stop or narrow if:

- reason codes are not understood
- false release concerns are material
- false constraints dominate the review
- metadata quality is poor
- integration overhead exceeds value

## Day 60: Recommend-Mode Criteria

Move from observe to recommend if:

- reviewers understand posture and reason codes
- useful constraint rate is meaningful to the customer
- false release candidate rate is within tolerance
- added review latency is acceptable
- existing approval process can display SMERC results

Do not move to recommend if:

- reviewers distrust the output
- SMERC adds no signal beyond current controls
- recommendations slow reviewers without improving judgment
- reason codes cannot be mapped to action

## Day 90: Enforcement-Readiness Criteria

Consider limited enforcement only if:

- customer security owner approves in writing
- candidate enforcement actions are narrow and well-defined
- false release and false constraint rates are acceptable
- control mapping is clear
- rollback or pause process is tested
- existing approvals and emergency overrides remain defined
- production impact is bounded

Do not enforce if:

- pilot evidence is weak
- reviewers disagree materially
- controls cannot be applied
- rollback process is untested
- action metadata is incomplete
- customer legal/security review is incomplete

## Expansion Criteria

Expand to another workflow if:

- first workflow produced useful evidence
- integration burden is repeatable
- customer has a second workflow with similar metadata
- sponsor confirms continued value

## Final Decision Options

At pilot close, choose one:

- no-go: stop and document why
- narrow: continue with smaller scope
- continue observe: more data required
- recommend mode: show SMERC to reviewers
- enforcement-readiness: design limited enforcement
- expand: add workflow or domain

## Evidence Standard

A go decision requires measured pilot evidence, not enthusiasm alone. A no-go decision is useful if it clarifies that recoverability scoring is not valuable, not differentiated, or not practical in the tested environment.
