# AWS Outcome Evaluation

`reference_engine.aws_outcome_evaluation` evaluates portable evidence emitted by SMERC's AWS proof paths.

It verifies record integrity, checks that execution evidence is coherent with the recorded posture, and distinguishes verified cleanup from cleanup that was not required or not proven. It deliberately does not calculate a decision-accuracy rate from SMERC's own output.

Decision correctness requires an independent reviewer label or incident outcome. Eligible records can be attached to the Decision Lifecycle Ledger and used for governed calibration review after that external label exists.

```powershell
python -m reference_engine.aws_outcome_evaluation proof-1.json proof-2.json --output reports/aws-outcome-evaluation.json
```

The evaluator accepts either a complete AWS proof containing `portable_evidence` or a portable evidence record directly. It does not call AWS, create resources, or alter policy.
