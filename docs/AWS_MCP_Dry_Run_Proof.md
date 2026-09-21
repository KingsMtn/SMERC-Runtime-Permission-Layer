# AWS MCP Authorization Dry-Run Proof

This runner binds SMERC enforcement to one fixed AWS sequence: discover the
default VPC, call `EC2.CreateSecurityGroup` with `DryRun=True`, and read back the
fixed sentinel group name. A success artifact is written only when AWS reports
`DryRunOperation` and the read-back finds zero resources.

```bash
python -m reference_engine.aws_mcp_dry_run_proof \
  --confirm-dry-run \
  --aws-resource-region us-east-1 \
  --output local-evidence/aws-mcp-dry-run-proof.json
```

The call has zero estimated incremental cost and must not create an AWS resource.
Authentication, policy, transport, unexpected AWS responses, or a nonzero read-back
count fail closed without a success artifact.

Success proves only that this observed authorization dry-run crossed SMERC before
AWS returned `DryRunOperation`, followed by a zero-resource read-back. It is not a
real mutation, rollback proof, production deployment, or proof that alternate AWS
access paths are blocked.
