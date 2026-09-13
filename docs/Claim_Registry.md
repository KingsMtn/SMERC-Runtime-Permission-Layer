# Claim Registry

## Purpose

The claim registry separates what SMERC evidence currently supports from what remains unproven.

It prevents the project from overstating customer validation, AWS readiness, production safety, or incident-reduction evidence.

## Run

```bash
python -m reference_engine.claim_registry --pretty
```

Generated outputs:

- `reports/claim_registry.json`
- `reports/Claim_Registry.md`

## Status Values

- `supported`: repository evidence supports this claim inside the stated boundary
- `partial`: repository evidence supports part of the claim but not the whole claim
- `not_supported`: the claim should not be made from current evidence

## Current Boundary

The registry can say SMERC has local proof paths, reject-first metadata intake, public-pattern fallback adapters, and an end-to-end reviewer flow.

It cannot say SMERC has customer validation, AWS endorsement, production certification, or incident-reduction proof.
