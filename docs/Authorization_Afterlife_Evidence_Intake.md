# Authorization-Afterlife Evidence Intake

This intake is the metadata boundary between a company-owned workflow and the Authorization-Afterlife Scenario Runner. It lets a reviewer provide 1 to 25 observations without AWS credentials, account identifiers, ARNs, payload contents, or raw API responses.

Each record declares its evidence class, source digest, observed authority epochs, revocation state, partial-effect state, settlement evidence, rollback availability, cost, scope, and limitations. The validator rejects unknown fields, duplicate evidence IDs, invalid digests, and credential-shaped keys anywhere in the manifest.

Run:

```text
python -m reference_engine.authorization_afterlife_evidence_intake examples/authorization_afterlife_evidence_manifest.json
```

The report identifies records that require consequence-time reconciliation. It validates shape and declared provenance only. It does not prove that upstream systems are truthful, that AWS attested the evidence, or that a workflow is safe for production.
