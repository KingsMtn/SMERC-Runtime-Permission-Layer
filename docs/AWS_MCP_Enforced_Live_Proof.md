# AWS MCP Enforced Live Proof

This runner is the next step after the supervised two-stage proof. It fixes the
action to the read-only, zero-estimated-cost `list_regions` tool and routes that
single observed call through runtime admission, SMERC recoverability policy,
the cost gate, and the constrained AWS managed MCP proxy executor.

Run only with a short-lived, read-only AWS credential available through the
standard AWS credential chain:

```bash
python -m reference_engine.aws_mcp_enforced_live_proof \
  --confirm-read-only \
  --aws-resource-region us-east-1 \
  --output local-evidence/aws-mcp-enforced-live-proof.json
```

The runner uses `mcp-proxy-for-aws-cli==1.7.0`. It writes a success artifact
only after the executor returns a successful MCP result. The artifact stores
the SMERC decision, exact target and argument binding, and result digest. It
does not store credentials or the raw AWS response.

Successful execution proves that this observed call crossed SMERC before the
configured executor returned success. It does not prove that all alternate AWS
paths are impossible, that AWS independently attested SMERC's decision, or that
the reference runner is production enforcement. Authentication, timeout, MCP,
or policy failure produces no success artifact.

The pinned proxy distribution is published by AWS's `aws-mcp-team` and freezes
its runtime dependency tree. Pinning is reproducibility control, not artifact
signature verification: <https://pypi.org/project/mcp-proxy-for-aws-cli/1.7.0/>
