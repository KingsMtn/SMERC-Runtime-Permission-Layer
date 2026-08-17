# SMERC Self-Governance Sandbox

## Purpose

The Self-Governance Sandbox answers a basic enterprise question:

> Who governs changes to the governance layer?

SMERC should not silently rewrite its own policies, thresholds, scoring weights, adapters, or enforcement logic.

Instead, proposed changes to SMERC itself should be:

- scored before activation
- capped to test-only when they look reasonable
- frozen or denied when evidence is weak
- reviewed by a human owner
- compared against before/after benchmarks
- recorded in the Decision Lifecycle Ledger
- rolled back if outcomes degrade

## Command

```bash
python -m reference_engine.self_governance_sandbox --pretty
```

Outputs:

```text
reports/self_governance_sandbox_report.json
reports/Self_Governance_Sandbox_Report.md
```

## What It Tests

The default examples evaluate three proposed SMERC changes:

1. Add a Runtime Evidence Trust Gate.
2. Lower the `ALLOW` threshold to increase automated releases.
3. Allow SMERC to rewrite its own scoring weights without human review.

The important rule:

> Even if base SMERC says a governance-layer change is recoverable enough to `ALLOW`, the sandbox caps it at `THROTTLE` / test-only until review, rollback, benchmark, and DLL evidence exist.

## Posture Meaning

| Self-Governed Posture | Meaning |
|---|---|
| `THROTTLE` | Test-only or shadow-mode change may proceed with review, benchmark comparison, rollback plan, and DLL recording. |
| `FREEZE` | Pause for design review before testing or activation. |
| `DENY` | Do not activate. The proposal is not structurally defensible. |
| `ESCALATE` | Require higher-level review before any action. |

The sandbox intentionally does not use unrestricted `ALLOW` for SMERC self-changes.

## What This Adds

This makes SMERC more credible as runtime permission infrastructure because it applies its own doctrine to itself:

> Capability does not equal permission.

That includes SMERC's own capability to change.

## Evidence Boundary

This is a synthetic self-governance proof module. It does not prove SMERC can autonomously improve itself, does not authorize self-training, and does not replace human review.

Its value is narrower:

> SMERC can preserve a governed path for policy evolution instead of allowing silent mutation of the governance layer.

