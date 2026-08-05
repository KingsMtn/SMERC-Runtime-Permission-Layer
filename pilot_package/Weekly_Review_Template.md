# SMERC Weekly Pilot Review Template

## Meeting Purpose

Review one week of SMERC pilot decisions, compare them with reviewer judgment, and decide whether the pilot should continue unchanged, narrow, expand, or stop.

## Attendees

- security owner
- platform engineering owner
- workflow owner
- pilot reviewers
- SMERC technical contact

## Weekly Inputs

Collect before the meeting:

- number of evaluated actions
- posture distribution
- top reason codes
- reviewer agreement rate
- override rate
- false release candidates
- false constraint candidates
- useful constraint examples
- latency impact
- integration issues
- confusing explanations

## Metrics Table

| Metric | This Week | Cumulative | Notes |
| --- | ---: | ---: | --- |
| Actions evaluated |  |  |  |
| `ALLOW` |  |  |  |
| `THROTTLE` |  |  |  |
| `FREEZE` |  |  |  |
| `DENY` |  |  |  |
| `ESCALATE` |  |  |  |
| Reviewer agreement rate |  |  |  |
| Override rate |  |  |  |
| False release candidates |  |  |  |
| False constraint candidates |  |  |  |
| Useful constraint rate |  |  |  |
| Median added latency |  |  |  |

## Decision Review

Review 3 to 5 representative decisions:

1. Most useful SMERC recommendation
2. Most questionable SMERC recommendation
3. Highest irreversible exposure action
4. Most common reason-code pattern
5. Any decision a reviewer would not trust

For each decision:

- replay ID:
- action:
- SMERC posture:
- reviewer view:
- final label:
- reason codes:
- controls:
- lesson:

## Open Issues

Track:

- missing metadata
- confusing reason codes
- excessive constraints
- insufficient constraints
- latency issues
- integration failures
- security concerns
- required documentation updates

## Weekly Decision

Choose one:

- continue unchanged
- continue with metadata changes
- narrow pilot scope
- expand to another workflow
- prepare recommend-mode test
- pause pilot
- stop pilot

## Action Items

| Owner | Action | Due Date |
| --- | --- | --- |
|  |  |  |

## Boundary Reminder

Weekly reviews are pilot evidence. They are not production accuracy claims. Any move toward enforcement requires explicit customer approval.
