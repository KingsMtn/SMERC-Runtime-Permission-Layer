# GitHub Actions Customer Pilot Intake Report

Generated: `2026-08-02T02:49:45+00:00`

## Decision

- Organization: `Prospect Platform Team`
- Workflow: `production-deployment`
- Ready for review call: `true`
- Ready for week-zero qualification: `false`
- Sample action count: `10`
- Retention days: `30`

## Customer Question

Can SMERC score these actions in observe mode without changing current approvals, then compare posture output with reviewer judgment for 30 days?

## Workflow Side Effects

- production deployment
- configuration change
- customer-visible release

## Existing Controls

- branch protection
- required review
- environment approval
- rollback runbook

## Blockers

- None.

## Warnings

- Business sponsor is not confirmed; this can be acceptable for technical review but may block paid pilot approval.

## Recommended Next Action

Schedule a review call and convert sample actions into smerc.customer-action-intake.v1 metadata.

## Evidence Boundary

Customer pilot intake only. It does not prove buyer demand, customer validation, production safety, incident reduction, compliance, or approval for enforcement.
