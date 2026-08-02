# SMERC CISO 5-Minute Proof Package

## Purpose

This page gives a CISO or delegated security leader the fastest serious way to evaluate SMERC.

The decision is not whether SMERC is production-certified.

The decision is:

> Is recoverability-aware runtime permissioning credible enough to test in observe mode against one GitHub Actions workflow?

## One-Sentence Claim

SMERC scores whether an AI-agent or automation action is recoverable enough to allow, throttle, freeze, deny, or escalate before execution.

## Why This Is Different From Normal Allow/Deny

Traditional controls often answer:

- Is this identity allowed?
- Does this policy permit the action?
- Did the approval workflow pass?

SMERC asks an additional runtime question:

- If this action goes wrong, can the organization contain it, roll it back, explain it, and learn from it?

That distinction matters when an action is technically authorized but operationally hard to undo.

## What Exists Today

SMERC currently includes working review artifacts:

- recoverability-aware Python scoring engine
- authenticated pilot API
- GitHub Actions observe-mode integration
- scoped workload identity and GitHub OIDC path
- SPARTa route layer for translating posture into tool behavior
- control mapping and evidence receipts
- Decision Lifecycle Ledger
- pilot review metrics
- generated governance reports
- test suite covering the engine, API, pilots, SPARTa, DLL, and GitHub integrations

## Five-Minute Review Path

| Minute | Review | Evidence |
| --- | --- | --- |
| 1 | Understand the product claim and limits. | `docs/Plain_English_Product_Overview.md` |
| 2 | See the current credibility evidence. | `reports/Credibility_Partner_Review_Packet.md` |
| 3 | Inspect the one-workflow pilot path. | `docs/GitHub_Actions_Pilot_Operator_Quickstart.md` |
| 4 | Check whether the pilot package is ready to start. | `reports/GitHub_Actions_Pilot_Readiness.md` |
| 5 | Decide whether to discuss a 30-day observe-mode pilot. | `pilot_package/First_Pilot_Path.md` |

## Current Readiness Signal

The current generated readiness report says the GitHub Actions pilot package is ready for:

- week-zero qualification
- one observe-mode workflow setup
- metadata-only action scoring
- weekly reviewer comparison
- day-30 stop, narrow, continue observe, or move-to-recommend decision

This is readiness for discussion and controlled pilot setup. It is not live customer validation.

## Pilot Ask

The narrow pilot ask is:

> Can we run SMERC in observe mode against one GitHub Actions workflow using metadata-only action descriptions and compare SMERC output with reviewer judgment for 30 days?

The first pilot should not block production workflows.

## What The Customer Provides

- one repository or workflow family
- one security owner
- one platform owner
- reviewer group
- metadata-only action descriptions
- weekly reviewer labels
- artifact retention decision
- stop conditions

## What SMERC Provides

- observe-mode GitHub Actions setup path
- action metadata examples
- posture, reason codes, and controls
- replayable decision artifacts
- pilot artifact summary
- reviewer comparison metrics
- final evidence package and go/no-go recommendation

## What Would Make This Interesting

SMERC is worth a pilot if a reviewer says:

- this resembles a real workflow risk
- current tools do not explicitly score recoverability before action
- constrained postures are more useful than simple allow/block in some cases
- metadata-only scoring is acceptable
- reviewer labels can be collected for 30 days

## What Would Kill The Pilot

Do not proceed if:

- there is no side-effecting workflow
- existing controls already score recoverability and rollback capacity well enough
- reviewers cannot label decisions
- metadata cannot be safely supplied
- the organization expects a production-certified enforcement platform immediately
- the recommended controls cannot map to the workflow

## Evidence Boundary

SMERC is ready for external technical review and bounded shadow-mode pilot discussion.

It should not be represented as production-certified, compliance-attested, customer-validated, or proven to reduce incidents until real pilot evidence supports those claims.
