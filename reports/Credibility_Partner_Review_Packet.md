# SMERC Credibility Partner Review Packet

Generated at: `2026-07-31T03:02:58+00:00`

## Purpose

This packet is for a serious external reviewer: CISO, security architect, platform engineering leader, reliability leader, or AI-governance lead.

The review question is narrow:

> Is SMERC credible enough to test in shadow mode against real workflow metadata?

## Positioning

- One sentence: SMERC is runtime permission infrastructure that scores whether automated actions are recoverable enough to execute before they create real side effects.
- Primary wedge: `GitHub Actions and AI-assisted software delivery shadow-mode pilot`
- Credibility partner ask: Review the evidence package, challenge the scenarios, and decide whether a metadata-only shadow-mode pilot is worth testing.

## Public Links

- GitHub repository: https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer
- Public demo home: https://admirable-sorbet-9986d5.netlify.app/
- CISO review page: https://admirable-sorbet-9986d5.netlify.app/ciso.html
- GitHub Actions pilot page: https://admirable-sorbet-9986d5.netlify.app/github-action.html

## What The Atlas Shows

- Pattern count: `5`
- Total scenarios: `40`
- Total deltas: `24`
- Weighted delta rate: `0.6`

| Discipline | Scenarios | Deltas | Delta Rate | Strongest Example |
| --- | ---: | ---: | ---: | --- |
| AML-inspired financial governance | 8 | 2 | 0.25 | `AML_CRYPTO_WITHDRAWAL_NEW_DEVICE` -> `FREEZE` |
| Change-management-inspired production governance | 8 | 7 | 0.875 | `CM_DATABASE_MIGRATION_WEAK_ROLLBACK` -> `DENY` |
| Security-response-inspired automation governance | 8 | 4 | 0.5 | `SR_SEND_CUSTOMER_BREACH_NOTICE` -> `DENY` |
| Model-risk-inspired AI governance | 8 | 6 | 0.75 | `MR_PROHIBITED_MODEL_EMAIL_SEND` -> `DENY` |
| SRE/incident-management-inspired reliability governance | 8 | 5 | 0.625 | `SRE_DELETE_QUEUE_BACKLOG` -> `DENY` |

## 30-Minute Review Path

| Time | Step | Evidence |
| --- | --- | --- |
| 0-5 | Read the claim and limits. | `docs/Plain_English_Product_Overview.md`, `docs/Governance_Pattern_Atlas.md` |
| 5-10 | Inspect the consolidated benchmark evidence. | `reports/Governance_Pattern_Atlas.md` |
| 10-15 | Inspect the recoverability scoring engine and action boundary. | `reference_engine/recoverability_engine.py`, `specification/SMERC_Action_Language_v1.md` |
| 15-20 | Inspect GitHub Actions pilot path and execution controls. | `pilot_package/GitHub_Actions_Pilot_Launch_Runbook.md`, `docs/SPARTa_Router_Operations.md` |
| 20-25 | Inspect replay and audit evidence. | `docs/Decision_Lifecycle_Ledger.md`, `docs/Governance_Report_Generator.md` |
| 25-30 | Answer pilot-fit questions and decide whether a credibility review should continue. | `pilot_package/Pilot_Evaluation_Checklist.md`, `pilot_package/Pilot_Handoff_Checklist.md` |

## Questions For The Reviewer

- Do the GitHub Actions and automation scenarios resemble actions your team sees or expects to see?
- Where would SMERC create useful restraint versus unnecessary noise?
- Which inputs would need customer-specific calibration before you would trust the scores?
- Which workflow should be tested first in shadow mode?
- What existing controls already solve this problem for you?
- Would replayable decision evidence help security, platform, audit, or incident review?
- What result would make you willing to continue from review into a bounded pilot?

## Pilot-Fit Questions

### Do AI agents or automation create deployment, infrastructure, security, data, finance, or customer-communication side effects?

- Strong fit signal: Yes, and those actions are increasing.
- Weak fit signal: No meaningful automated side effects exist yet.

### Can the first pilot run in shadow mode without blocking production?

- Strong fit signal: Yes, scoring can observe and compare against reviewer judgment.
- Weak fit signal: No, the organization requires immediate enforcement or no access at all.

### Can the prospect provide metadata-only examples without secrets or customer data?

- Strong fit signal: Yes, action descriptions and risk metadata can be shared safely.
- Weak fit signal: No, even sanitized workflow metadata cannot be shared.

### Is there an accountable security, platform, or AI-governance reviewer?

- Strong fit signal: Yes, a named reviewer can label agreement, false release, false restraint, and useful restraint.
- Weak fit signal: No owner exists for review labels or go/no-go decisions.

### Would recoverability scoring be judged separately from existing allow/deny policy?

- Strong fit signal: Yes, the team wants to test whether recovery capacity changes decisions.
- Weak fit signal: No, the team only wants identity/access policy or generic AI guardrails.

## What SMERC Is Not Claiming

- SMERC is not production-certified.
- SMERC is not customer-validated yet.
- SMERC is not a replacement for OPA, IAM, GRC, SIEM, SOAR, EDR, ServiceNow, Jira, AML, or model-risk systems.
- SMERC is not claiming incident reduction, compliance attestation, or product-market fit.
- SMERC should begin in shadow mode before any enforcement pilot.

## Desired Partner Response

- The scenarios resemble a real workflow we care about.
- The deltas are useful enough to test rather than only interesting on paper.
- We can provide metadata-only examples for shadow-mode scoring.
- A named reviewer can compare SMERC output against human judgment.
- A 30-day or 90-day bounded pilot is worth discussing.

## Suggested Outreach Paragraph

I am looking for a credibility review of SMERC, a runtime permission layer for AI-agent and automation actions. The current prototype scores whether proposed actions are recoverable enough to allow, throttle, freeze, deny, or escalate before execution. The first pilot wedge is GitHub Actions shadow-mode scoring for AI-assisted code, deployment, and infrastructure workflows. I am not asking you to treat this as production-ready. I am asking whether the evidence package is credible enough to test against metadata-only examples from a real workflow.
