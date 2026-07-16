# SMERC 30/60/90 Day Pilot Plan

## Overview

This plan moves from low-risk observation to evidence-based recommendation. Enforcement is optional and should occur only after customer approval.

## Day 0: Readiness

Complete before the pilot clock starts:

- scope one workflow or workflow family
- complete customer questionnaire
- approve data boundary
- identify reviewers
- confirm stop conditions
- confirm success metrics
- choose local, customer-hosted, or hosted deployment

## Days 1-30: Observe

Goal:

Run SMERC in shadow mode without changing execution behavior.

Activities:

- generate action metadata
- call SMERC for each in-scope action
- store decisions and replay IDs
- collect reviewer labels
- hold weekly review
- identify metadata gaps

Success criteria:

- at least one workflow producing usable metadata
- decisions are replayable
- reviewers understand posture and reason codes
- no sensitive data boundary violation
- no production workflow disruption

Deliverables:

- week 1 setup note
- weekly review notes
- posture distribution
- initial reviewer agreement metrics
- integration gap list

## Days 31-60: Recommend

Goal:

Surface SMERC recommendations to reviewers while existing controls remain authoritative.

Activities:

- show SMERC posture in existing review process
- compare reviewer decision before and after seeing SMERC where possible
- tune metadata collection
- evaluate whether reason codes are actionable
- identify candidate controls for `THROTTLE`, `FREEZE`, and `ESCALATE`

Success criteria:

- reviewers find at least some constraints useful
- false release concerns remain within customer tolerance
- false constraint noise remains within customer tolerance
- recommendations do not materially slow normal review
- customer can identify where SMERC adds signal beyond existing controls

Deliverables:

- recommendation-mode findings
- useful constraint examples
- false release and false constraint analysis
- updated integration plan

## Days 61-90: Enforcement Readiness

Goal:

Decide whether limited enforcement is justified.

Activities:

- define narrow enforcement candidates
- test non-production enforcement if approved
- evaluate SPARTa routes or adapter controls where relevant
- prepare final evidence package
- recommend stop, narrow, expand, or enforce-limited

Success criteria:

- customer can name actions where SMERC should influence execution
- controls are enforceable or gaps are clearly documented
- reviewer agreement and false-release metrics are acceptable
- security owner approves any enforcement path in writing

Deliverables:

- final pilot report
- evidence package
- go/no-go decision
- next-scope recommendation
- unresolved risk register

## Pilot Modes

Observe:

- SMERC records decisions
- no workflow behavior changes

Recommend:

- SMERC recommendations are visible to reviewers
- existing approvals remain authoritative

Enforce-readiness:

- SMERC identifies candidate enforcement policies
- production enforcement remains blocked unless separately approved

Limited enforce:

- narrow non-production or low-risk production path only
- explicit written approval required

## Exit Options

At day 30, 60, or 90, customer may choose:

- stop: insufficient value or unacceptable burden
- narrow: useful but scope too broad
- continue observe: more data needed
- move to recommend: evidence supports reviewer visibility
- test enforcement-readiness: evidence supports controlled enforcement design
- expand: add workflow or domain
