# SMERC End-To-End PR Guardian Demo

This demo connects the current SMERC modules into one reviewable workflow for an AI-assisted pull request.

```text
AI-assisted PR request
-> SMERC runtime decision
-> PR Guardian comment and certificate
-> SPARTa route
-> Decision Lifecycle Ledger
-> DLL Intelligence summary
```

## Why It Exists

SMERC now has multiple working components. This demo proves they can operate as one pilot-grade governance loop instead of a collection of disconnected artifacts.

It is designed for technical reviewers, CISOs, and design partners who want to see:

- what action was requested
- what SMERC decided
- what would appear in a pull request
- how SPARTa routes the posture
- how the Decision Lifecycle Ledger records the lifecycle
- what DLL Intelligence learns from the verified record

## Run It

```bash
python -m reference_engine.end_to_end_pr_guardian_demo --pretty
```

The command writes:

- `reports/End_To_End_PR_Guardian_Demo.md`
- `reports/end_to_end_pr_guardian_demo.json`
- `reports/end_to_end_pr_guardian_comment.md`
- `reports/end_to_end_pr_guardian_certificate.json`
- `reports/end_to_end_pr_guardian_sparta_route.json`
- `reports/end_to_end_pr_guardian_dll.json`
- `reports/end_to_end_pr_guardian_dll_intelligence.json`

## What The Default Scenario Shows

The default scenario is an AI coding agent proposing changes to authentication middleware and deployment configuration in a pull request.

SMERC evaluates the action, PR Guardian renders the visible review artifact, SPARTa routes the decision into accountable review behavior, the Decision Lifecycle Ledger records the lifecycle, and DLL Intelligence produces a governance learning summary.

## Boundary

This is a synthetic end-to-end demo. It does not prove customer demand, incident reduction, production safety, or compliance readiness.

The correct commercial use is shadow-mode pilot discussion: a customer can replace the synthetic action with real pull-request metadata, collect reviewer agreement, and measure whether SMERC creates useful decision evidence before enforcement.
