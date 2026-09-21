# AWS Reversible Mutation Proof

The fixed runner creates one empty tagged EC2 security group in the default VPC,
deletes it immediately, measures rollback latency, and verifies zero residual
groups. It requires an explicit operator confirmation flag and estimates zero
incremental AWS cost.

The approval is injected into trusted adapter configuration and bound to the
exact server, tool, and argument digest. It is not accepted from the MCP caller.

```bash
python -m reference_engine.aws_reversible_mutation_proof \
  --confirm-reversible-mutation \
  --aws-resource-region us-east-1 \
  --output local-evidence/aws-reversible-mutation-proof.json
```

No success artifact is written unless SMERC allows the exact fixed script, AWS
reports successful creation and deletion, and read-back finds zero residual state.
The repository also contains a sanitized connector-observed result in
`reports/aws_reversible_mutation_observation.json`; it is explicitly not claimed
as transport-enforced SMERC evidence.
