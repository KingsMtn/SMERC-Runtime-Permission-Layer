# SMERC Fallback Policy Layer

## Purpose

Enterprise reviewers will ask:

> What happens when SMERC cannot decide?

The Fallback Policy Layer provides a deterministic fail-safe answer for unavailable, stale, incomplete, conflicting, or timeout-prone evidence.

## What It Handles

The layer evaluates:

- SMERC API unavailable
- content scanner unavailable
- metadata incomplete
- stale policy bundle
- stale evidence
- conflicting evidence
- unknown tool
- execution adapter unavailable
- timeout
- review queue unavailable
- rollback plan missing

## What It Returns

The layer returns:

- proposed posture
- fallback posture
- whether fallback was applied
- failure type
- high-impact indicator
- reason codes
- controls
- plain-English summary

## Deterministic Rule

Fallback policy should only preserve or restrict posture. It should not make an action less restrictive than the proposed SMERC decision.

Examples:

- `ALLOW` plus stale policy becomes `FREEZE`.
- `THROTTLE` plus missing rollback for high-impact money movement becomes `DENY`.
- `THROTTLE` plus unavailable content scanner for destructive data action becomes `FREEZE`.
- `FREEZE` plus unavailable review queue for high-impact action becomes `DENY`.
- Low-risk test action with no failure remains `ALLOW`.

## Why This Matters

This closes a practical enterprise objection:

> If your governance layer is unavailable, stale, or missing evidence, does automation continue?

SMERC's answer should be:

> No. It fails safe according to explicit policy for the action class.

## Run

```bash
python -m reference_engine.fallback_policy --pretty
```

Generated outputs:

```text
reports/fallback_policy_report.json
reports/Fallback_Policy_Layer_Report.md
```

## Evidence Boundary

This layer is deterministic failure handling. It is not production validation, compliance attestation, incident-reduction proof, or a substitute for customer-owned policy review.

