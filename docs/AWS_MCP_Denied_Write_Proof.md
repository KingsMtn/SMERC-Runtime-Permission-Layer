# AWS MCP Denied Write Proof

This zero-cost proof presents SMERC with a concrete `delete_bucket` request whose
recoverability evidence is intentionally unacceptable. Runtime admission succeeds,
then recoverability policy must return `DENY`, route the request to `BLOCK`, and
leave the configured AWS executor untouched.

```bash
python -m reference_engine.aws_mcp_denied_write_proof \
  --output local-evidence/aws-mcp-denied-write-proof.json
```

The bucket name is a fixed proof sentinel. The runner has no live AWS executor and
uses a tripwire executor that fails if called. It therefore creates no AWS resource,
changes no AWS state, requires no AWS credentials, and has no estimated AWS charge.

The resulting artifact proves that this destructive request was blocked before the
configured execution boundary. It does not prove that AWS independently enforced
the decision or that alternate AWS access paths are unavailable.
