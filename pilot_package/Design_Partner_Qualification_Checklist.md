# SMERC Design Partner Qualification Checklist

## Purpose

This checklist helps decide whether a company is a good early SMERC design partner.

The goal is not to convince every interested company to run a pilot. The goal is to find organizations that can generate useful evidence about whether recoverability-aware runtime permission scoring improves governance decisions.

## Ideal Design Partner

An ideal design partner has:

- AI agents, copilots, scripts, or automation near real side effects
- GitHub Actions, CI/CD, infrastructure, security, or deployment workflows in scope
- existing human review or approval process
- concern about rollback, blast radius, containment, or irreversible change
- security or platform owner willing to review evidence weekly
- ability to run metadata-only observe mode
- willingness to label reviewer agreement, false release, false constraint, and useful constraint
- patience for a pilot-grade system that is not production-certified

## Disqualifiers

Do not pursue a pilot if:

- the prospect wants immediate production enforcement without evidence
- no human reviewer can participate
- the only available workflow requires raw secrets, regulated payloads, or customer data
- the prospect expects compliance certification
- the prospect cannot define success or stop conditions
- there is no owner for the workflow
- existing controls already provide replayable decisions, reviewer labels, outcome tracking, and recoverability analysis with less burden

## Qualification Questions

Ask before offering a paid pilot:

1. What AI agents, copilots, bots, scripts, or automations can trigger meaningful side effects today?
2. Which workflow is most suitable for observe-mode scoring?
3. Who owns that workflow?
4. Who owns security approval for a pilot?
5. Who owns platform or DevSecOps implementation?
6. Can action metadata be generated without raw secrets, customer data, private prompts, or full source contents?
7. What current approval path exists?
8. What decisions are hard to explain or replay after the fact?
9. What failures would be hard to reverse?
10. Can reviewers label agreement, overrides, false release candidates, false constraint candidates, and useful constraints?
11. How often can reviewers meet or submit feedback?
12. What would make the pilot a no-go?
13. What would justify continuing from observe to recommend mode?
14. What would justify stopping after 30 days?
15. What evidence would make the CISO care?

## Scoring

Score each category from 0 to 3.

| Category | 0 | 1 | 2 | 3 |
| --- | --- | --- | --- | --- |
| Workflow fit | No side-effecting automation | Low-impact automation only | One meaningful workflow | Multiple meaningful workflows |
| Recoverability pain | Not a concern | Occasional concern | Frequent concern | Executive/security concern |
| Metadata readiness | Cannot provide metadata | Manual metadata only | Partial automation | Reliable metadata path |
| Reviewer capacity | None | Ad hoc | Weekly reviewer available | Dedicated reviewer group |
| Buyer ownership | Unknown | Technical curiosity only | Manager sponsor | CISO/security owner engaged |
| Data boundary | Requires sensitive data | Boundary unclear | Metadata-only likely | Metadata-only approved |
| Measurement readiness | No metrics | Basic counts only | Reviewer labels possible | Labels, outcomes, latency, and rollback data possible |
| Pilot urgency | No urgency | Research interest | Near-term governance concern | Active AI-agent risk or rollout |

## Fit Bands

| Score | Fit | Recommendation |
| ---: | --- | --- |
| 0-8 | Weak fit | Do not pursue a paid pilot. Offer public materials only. |
| 9-15 | Exploratory fit | Offer technical review or a narrow unpaid/low-cost scoping call. |
| 16-21 | Moderate fit | Offer a 30-day shadow-mode pilot if reviewer time is confirmed. |
| 22-24 | Strong fit | Offer a 90-day design partner pilot with DLL evidence package. |

## Recommended Offer By Fit

| Fit | Offer |
| --- | --- |
| Weak fit | Public repo and self-guided review only. |
| Exploratory fit | CISO Technical Review, free to `$2,500`. |
| Moderate fit | 30-Day Shadow-Mode Pilot, `$7,500-$15,000`. |
| Strong fit | 90-Day Design Partner Pilot, `$25,000-$50,000`. |

## Evidence To Confirm Before Contracting

Before a paid pilot starts, confirm:

- workflow owner
- security owner
- reviewer list
- data boundary approval
- action metadata source
- artifact retention period
- weekly review cadence
- success metrics
- stop conditions
- go/no-go decision owner

## Design Partner Boundary

A design partner is not a customer reference by default. Do not use the company's name, results, screenshots, or workflow details externally unless the company approves that use in writing.

Do not treat design-partner interest as proof of product-market fit. The design partner is evidence collection, not the final market answer.

