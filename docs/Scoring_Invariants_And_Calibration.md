# Scoring Invariants And Calibration

## Purpose

SMERC uses explicit scoring math to support runtime permission decisions. The current formulas are pilot-grade reference formulas, not customer-calibrated production thresholds.

The scoring-invariants layer answers a narrower but important question:

> Do the current formulas obey the safety properties SMERC claims they should obey?

## What Is Tested

`reference_engine/scoring_invariants.py` evaluates declared invariants for the Recoverability Engine and the Model and Agent Fitness Layer.

The recoverability invariants check that:

- higher reversibility does not increase irreversible exposure
- higher reversibility does not reduce reversible capacity or authorization score
- higher rollback latency does not reduce exposure or operational stress
- lower evidence validity does not increase confidence or authorization
- higher anomaly pressure does not increase confidence or reduce stress
- external side effects and sensitive data do not reduce irreversible exposure

The Model and Agent Fitness invariants check that:

- data-boundary violations fail closed
- tool-authority gaps fail closed
- required-capability gaps fail closed
- higher task risk does not increase the risk-adjusted executor score
- stronger safety history does not reduce model fitness for an otherwise identical qualified executor

## Why This Matters

These tests make the score behavior more defensible. They show that the formulas are not arbitrary text labels and that key safety assumptions are executable.

They also help prevent future changes from accidentally making SMERC less restrained. If a weight or threshold change breaks a declared invariant, the test suite should fail before the change reaches a reviewer or pilot.

## What This Does Not Prove

The invariant suite does not prove:

- production incident reduction
- calibrated customer thresholds
- financial-risk prediction
- general model intelligence
- that any action is safe in a real environment

Those require design-partner evidence, reviewer agreement data, false release/constraint analysis, latency measurement, and incident or near-miss correlation.

## Run

```bash
python -m reference_engine.scoring_invariants --pretty
python -m reference_engine.scoring_invariants \
  --json-output reports/scoring_invariants_results.json \
  --markdown-output reports/Scoring_Invariants_Report.md
python -m unittest tests.test_scoring_invariants -v
```

## Calibration Path

The right calibration path is:

1. Keep invariant tests mandatory.
2. Run SMERC in shadow mode against real workflows.
3. Collect reviewer agreement, overrides, false releases, false constraints, latency, and recoverability outcomes.
4. Adjust thresholds only with versioned policy records.
5. Preserve the old and new policy versions for replay comparison.
6. Avoid claiming production readiness until the evidence program supports it.
