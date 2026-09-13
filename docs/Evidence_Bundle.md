# Evidence Bundle

## Purpose

The evidence bundle binds key SMERC proof artifacts by path, byte size, and SHA-256 digest.

It is inspired by verifiable evidence bundle patterns in adjacent agent reliability work, but remains deliberately narrow: it verifies local artifact integrity, not customer validation.

## Run

```bash
python -m reference_engine.claim_registry --pretty
python -m reference_engine.evidence_bundle build --pretty
python -m reference_engine.evidence_bundle verify reports/evidence_bundle.json
```

Generated outputs:

- `reports/evidence_bundle.json`
- `reports/Evidence_Bundle.md`

## What It Verifies

- expected artifact paths exist
- artifact byte sizes match
- artifact SHA-256 digests match
- bundle schema has no unknown top-level fields
- artifact records have no unknown fields

## What It Does Not Verify

- customer validation
- production safety
- AWS endorsement
- official benchmark score
- incident reduction
- compliance status
- correctness of every underlying SMERC decision
