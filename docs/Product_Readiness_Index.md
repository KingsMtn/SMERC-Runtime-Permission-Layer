# SMERC Product Readiness Index

## Purpose

This index keeps the product path blunt. It separates what SMERC has already earned from what still needs customer evidence before the project should be described as a product.

Current status:

> Pilot-grade product candidate. Ready for metadata-only shadow-mode review. Not yet a production product.

## Readiness Scorecard

| Area | Current State | Product Blocker | Proof Needed | Next Action |
| --- | --- | --- | --- | --- |
| Core decision engine | Implemented and tested. Scores recoverability, evidence, side effects, impact, autonomy, and execution-boundary weakness. | Needs external calibration against real workflow metadata. | 5 to 25 customer-owned actions from one workflow with reviewer labels. | Keep core engine stable while collecting reviewer deltas. |
| AWS shadow-mode lane | Implemented as metadata-only adapters, reviewer bundles, decision API surface, action-chain proof, postcondition evidence, and environment-boundary intake. | No external AWS workflow owner has supplied replacement metadata yet. | One AWS-style reviewer replaces examples with safe metadata from an owned workflow. | Lead with AWS metadata pilot request and one-action reviewer ask. |
| Intake friction | GitHub issue templates, JSON templates, local reports, GitHub Actions customer evaluation path, and pilot intake docs exist. | Too many possible entry points may confuse reviewers. | A reviewer can complete one intake path without live help. | Create one preferred product front door and keep other docs secondary. |
| Buyer-facing proof packet | Serious reviewer bundle, AWS reviewer bundle, CISO packets, and product docs exist. | Proof is broad and document-heavy. | One short artifact that shows problem, input, decision, report, pilot offer, and boundary. | Create a single product proof packet that points to deeper evidence. |
| Posture language | `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, and `ESCALATE` are implemented as decision outcomes with controls and reason codes. | Postures need clearer product-role framing. | Reviewers understand what each posture does operationally. | Describe postures as specialized decision roles, not as vague labels. |
| Execution-boundary evidence | Implemented in intake, AWS adapter, recoverability metadata contract, and core engine scoring floors. | Needs real-world examples of weak and strong execution boundaries. | Reviewer-supplied rows with tooling, host, network, sandbox surface, and boundary context. | Keep asking: where will it execute, and can that boundary contain failure? |
| Pilot operation | API, audit store, review queue, metrics, console, and report generators exist. | Needs an actual shadow-mode run with reviewer time, decisions, and labels. | 30-day pilot or shorter controlled review with denominator-aware metrics. | Package a 30-day metadata-only pilot offer. |
| Commercial boundary | Field-of-use strategy, license/commercial-use boundary, moat docs, and buyer maps exist. | Needs legal review before serious acquisition, licensing, or enterprise sale. | Counsel-reviewed license/commercial terms and field-of-use carve-outs. | Keep AWS/cloud package separable from future finance, insurance, crypto, and other verticals. |
| Deployment | Docker, Render, API docs, and GitHub Action integration exist. | Netlify production deploys may be paused by credits; production hardening is incomplete. | Stable deploy target plus documented operator setup and rollback. | Do not let Netlify delay code progress; use GitHub and local proof as source of truth. |
| External credibility | OpenSSF feedback was answered; public learning maps and benchmark/fallback paths exist. | Still needs independent reviewer validation or design-partner signal. | At least one credible outside reviewer says the shadow-mode review is useful. | Continue narrow outreach after the proof packet is clean. |

## Product Claim Ladder

Use the strongest accurate claim:

1. **Project:** SMERC is a recoverability-first runtime governance project.
2. **Technical artifact:** SMERC has runnable engine, API, adapters, reports, tests, and decision evidence.
3. **Pilot-grade product candidate:** SMERC can run a metadata-only shadow-mode review for one workflow.
4. **Enterprise beta:** SMERC has at least one external pilot or strong reviewer-owned metadata evaluation.
5. **Product:** SMERC has paying or committed users, operating support, security review, deployment reliability, and measured customer value.

Current claim:

> SMERC is a pilot-grade product candidate for metadata-only shadow-mode recoverability review.

Do not claim:

- production-certified security platform
- proven incident reduction
- regulatory compliance
- AWS endorsement
- enterprise beta
- acquisition-ready asset without diligence

## Next Product Moves

1. Create one buyer-facing product proof packet.
2. Make the AWS metadata pilot request the preferred external ask.
3. Collapse duplicate front doors into one primary path.
4. Add posture-role framing for `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, and `ESCALATE`.
5. Ask for one reviewer-owned 5-to-25 action dataset.
6. Run the 30-day shadow-mode pilot only after a reviewer says the report is useful.

## Work / Result / Impact

Work: convert SMERC's scattered project evidence into a product-readiness scoreboard.

Result: reviewers and the builder can see what is complete, what still blocks product status, and what evidence moves the project forward.

Impact: SMERC stays ambitious without overclaiming. The path from project to product becomes measurable instead of emotional.
