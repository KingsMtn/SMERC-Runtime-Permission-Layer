# AWS Final Proof Package

The final proof package combines three bounded evidence classes:

1. An allowed read that crossed SMERC and the configured AWS MCP transport.
2. A destructive write denied before the configured executor was called.
3. A reversible mutation that created and deleted one empty security group and verified zero residual state.

The package verifies portable evidence for the read and mutation, evaluates decision/execution coherence and cleanup, binds artifact digests, and rejects declared incremental cost above the operator's cap. It does not make live AWS calls itself.

## Build a package

```powershell
python -m reference_engine.aws_final_proof_package `
  --read-proof artifacts/aws-read.json `
  --denied-write-proof artifacts/aws-denied-write.json `
  --mutation-proof artifacts/aws-reversible-mutation.json `
  --cost-cap-usd 1.00 `
  --output artifacts/aws-final-proof-package.json
```

Without authenticated independent labels, the result is `TECHNICALLY_COMPLETE_AWAITING_EXTERNAL_LABELS`. That means the observed behavior, enforcement coherence, and cleanup evidence passed, but SMERC has not awarded itself an accuracy claim.

After an independent reviewer creates labels with `aws_external_outcome_label.py`, pass each file with `--external-label` and provide the verification key through `SMERC_EXTERNAL_LABEL_KEY`. Full eligible-record coverage changes the package status to `INDEPENDENTLY_VALIDATED`.

## Boundary

This package is not an AWS attestation, a billing statement, or proof that every AWS access path is mediated by SMERC. The denied-write tripwire proves behavior at the configured local enforcement boundary. Production claims require broader deployment evidence and independent operational review.
