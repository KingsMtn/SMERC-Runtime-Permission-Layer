# Governance Pattern Atlas

The Governance Pattern Atlas is the consolidation layer for SMERC's current benchmark work.

It answers a simple question:

> Is SMERC one coherent runtime permission system, or a collection of disconnected governance ideas?

The answer should be judged by whether the same mechanism appears across different enterprise operating models:

- recoverability-weighted authorization
- irreversible exposure
- reversible capacity
- runtime posture
- reason codes
- controls
- replayable decision evidence

## Included Patterns

The atlas currently consolidates:

- AML-inspired financial governance
- change-management-inspired production governance
- security-response-inspired automation governance
- model-risk-inspired AI governance
- SRE/incident-management-inspired reliability governance

Each pattern has its own benchmark and evidence boundary.

## Generate The Atlas

```bash
python -m reference_engine.governance_pattern_atlas --pretty
```

Generated outputs:

- `reports/Governance_Pattern_Atlas.md`
- `reports/governance_pattern_atlas.json`

## How To Read It

Use the atlas before asking for external review.

It shows:

- total scenario count across the pattern family
- weighted delta rate
- strongest examples
- what SMERC adds
- what SMERC does not replace
- what a credibility partner should challenge

## Evidence Boundary

The atlas is a synthetic/proxy evidence summary.

It is not customer validation, product-market fit, production certification, compliance attestation, incident-reduction proof, or proof that any buyer will purchase SMERC.

## Why It Matters

SMERC should not be pitched as governance for everything.

The atlas shows a narrower, more credible claim:

> Many enterprise governance systems leave a gap at the moment an automated action is about to execute. SMERC fills that gap by scoring recoverability before execution.

That is the story to take to credibility partners.
