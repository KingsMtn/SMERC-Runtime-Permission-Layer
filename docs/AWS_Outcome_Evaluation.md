# AWS Outcome Evaluation

`reference_engine.aws_outcome_evaluation` evaluates portable evidence emitted by SMERC's AWS proof paths.

It verifies record integrity, checks that execution evidence is coherent with the recorded posture, and distinguishes verified cleanup from cleanup that was not required or not proven. It deliberately does not calculate a decision-accuracy rate from SMERC's own output.

Decision correctness requires an independent reviewer label or incident outcome. Eligible records can be attached to the Decision Lifecycle Ledger and used for governed calibration review after that external label exists.

Authenticated external labels use `smerc.aws-external-outcome-label.v1`. Each label is bound to the exact portable-evidence payload digest and authenticated with a reviewer-controlled HMAC key. This proves possession of that shared key, not organizational independence or public-key identity; those remain pilot governance responsibilities.

```powershell
python -m reference_engine.aws_outcome_evaluation proof-1.json proof-2.json --output reports/aws-outcome-evaluation.json
```

To include authenticated external labels, put the shared pilot verification secret in an environment variable rather than command history:

```powershell
$env:SMERC_EXTERNAL_LABEL_KEY = "use-a-secret-of-at-least-32-bytes"
python -m reference_engine.aws_outcome_evaluation proof.json --external-label reviewer-label.json --output reports/aws-outcome-evaluation.json
```

The evaluator accepts either a complete AWS proof containing `portable_evidence` or a portable evidence record directly. It does not call AWS, create resources, or alter policy.
