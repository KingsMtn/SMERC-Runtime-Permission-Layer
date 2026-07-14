# SMERC Decision Certificate v1

SMERC Decision Certificate v1 turns a verified Decision Lifecycle Ledger into a portable, digest-bound decision artifact.

The certificate is intended for pilot review, CISO inspection, replay, and integration testing. It summarizes what was requested, what evidence existed, what SMERC recommended, what a human did, what executed, what outcome was observed, and whether learning recommendations remain review-only.

## Why It Exists

Traditional logs usually say what happened. A SMERC Decision Certificate is designed to preserve why a consequential action was authorized, constrained, blocked, or escalated.

The certificate binds:

- the decision ID
- tenant ID
- Decision Lifecycle Ledger version
- record count
- ledger head record hash
- request summary
- evidence summary
- SMERC evaluation
- human interaction summary
- execution summary
- outcome summary
- learning recommendation summary
- optional SPARTa route-report digest

## What It Proves

The reference implementation can show:

- the source DLL verified at certificate issuance time
- the certificate digest changes if summarized certificate content changes
- an optional HMAC signature matches the certificate digest
- an optional SPARTa route report still matches the certificate route binding
- an optional source DLL still matches the certificate lifecycle binding

## What It Does Not Prove

This certificate does not, by itself, provide:

- immutable storage
- legal recordkeeping
- regulatory retention
- public-key non-repudiation
- managed enterprise key custody
- independent proof that source-system facts were accurate
- automatic policy activation from learning recommendations

Those are deployment, security, evidence-retention, and legal-review requirements for a production system.

## Generate An Example

```powershell
python -m reference_engine.decision_certificate `
  --ledger reports/decision_lifecycle_ledger_example.json `
  --signing-key "local-certificate-signing-key-012345" `
  --key-id "local-demo-key" `
  --verify `
  --json-output reports/decision_certificate_example.json `
  --markdown-output reports/Decision_Certificate_Example.md `
  --pretty
```

## Product Role

Decision Certificate v1 is the bridge between runtime authorization and enterprise review.

It lets a reviewer ask:

- What was the action?
- Who or what initiated it?
- What did SMERC know at the time?
- What posture did SMERC recommend?
- Did a human accept, modify, override, or ignore the recommendation?
- What actually executed?
- Was rollback available or used?
- Was the outcome judged correct?
- What policy updates were suggested, and are they still pending review?

## Current Boundary

This is a pilot-grade artifact. It is suitable for demonstrating replayable governance and tamper-evident summaries. It should not be described as a certified compliance ledger, immutable audit database, or production evidence vault without additional implementation and legal/security review.
