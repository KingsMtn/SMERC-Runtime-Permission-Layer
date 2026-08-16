# GitHub Actions Pilot Installer

The GitHub Actions Pilot Installer is the current self-contained "vehicle" demo for SMERC.

It does not install SMERC into a customer's production workflow. It generates the complete artifact folder a reviewer should expect from a shadow-mode GitHub Actions pilot:

```text
SPARK evidence
  -> Action Language
  -> Constraint Eligibility
  -> SMERC decision
  -> SPARTa route
  -> Decision Lifecycle Ledger
  -> DLL Intelligence
  -> Timing Evidence
  -> pilot briefing
```

## Run

```bash
python -m reference_engine.github_actions_pilot_installer --output-dir reports/github_actions_pilot_package --pretty
```

The generated folder includes:

| File | Purpose |
| --- | --- |
| `README.md` | Reviewer-facing pilot briefing. |
| `pilot_package.json` | Complete assembled package. |
| `spark_intake_report.json` | Non-secret signal intake and compiled action envelope. |
| `constraint_eligibility.json` | Hard policy and authority gate before recoverability scoring. |
| `effective_decision.json` | SMERC runtime decision after eligibility is applied. |
| `sparta_route.json` | Route state and controls for the declared GitHub Actions plan. |
| `decision_lifecycle_ledger.json` | Hash-chain lifecycle evidence. |
| `dll_intelligence.json` | Review-gated learning and evidence summary. |
| `timing_report.json` | Timing, rollback, cancellation, and unavailable-evaluation report. |

## What It Proves

- The current SMERC parts can run as one connected pilot loop.
- Constraint Eligibility is applied before recoverability can soften posture.
- SPARTa receives the effective posture and routes the GitHub Actions plan.
- DLL records request, evidence, evaluation, review, execution, outcome, and learning events.
- Timing Evidence is included in the review package instead of being treated as a side note.

## What It Does Not Prove

- It does not prove production readiness.
- It does not prove customer demand.
- It does not prove incident reduction.
- It does not prove that customer workflow evidence is truthful.
- It does not replace GitHub branch protection, deployment approvals, IAM, OPA, SIEM, GRC, or human accountability.

## Customer Pilot Upgrade Path

To turn this into a real pilot:

1. Choose one GitHub Actions workflow with meaningful side effects.
2. Keep SMERC in observe mode.
3. Replace the default SPARK example with customer-approved non-secret workflow metadata.
4. Collect reviewer labels for agreement, disagreement, false release, false constraint, and useful constraint.
5. Measure median and p95 decision latency, workflow overhead, unavailable evaluations, and reviewer burden.
6. Consider recommend or enforce mode only after the evidence supports it.

The checked-in example package is at `reports/github_actions_pilot_package/`.
