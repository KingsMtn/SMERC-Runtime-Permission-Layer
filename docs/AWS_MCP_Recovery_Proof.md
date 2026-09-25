# AWS MCP Recovery Proof

This deterministic proof exercises an AWS-shaped CloudFormation `update_stack` MCP call through the enforced recovery boundary and normal Runtime Assurance transport chain.

It compares three cases:

1. Missing recovery evidence is denied before ordinary governance routing.
2. Stale recovery evidence is frozen before ordinary governance routing.
3. Verified, scoped recovery evidence is admitted to ordinary governance but receives no execution authority.

Run:

```powershell
python -c "import json; from reference_engine.aws_mcp_recovery_proof import run_proof; print(json.dumps(run_proof(), indent=2))"
```

## Evidence Boundary

The proof is local, synthetic, metadata-only, and zero-spend. It does not call AWS, create or modify AWS resources, prove that CloudFormation rollback succeeds, provide AWS attestation, or establish production readiness. Its narrow claim is that SMERC enforces recovery-evidence ordering correctly on an AWS-shaped MCP mutation.
