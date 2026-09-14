# TRACE-Style Evidence Adapter

## Purpose

This adapter is a future-shape proof for how SMERC could consume runtime evidence metadata inspired by TRACE-style attestation and compliance evidence.

It does not implement TRACE.

It does not verify hardware attestation.

It shows how metadata-only runtime evidence can become SMERC postcondition evidence.

## Run

```bash
python -m reference_engine.trace_evidence_adapter --pretty
```

This writes:

- `reports/trace_evidence_adapter/TRACE_Evidence_Adapter_Report.md`
- `reports/trace_evidence_adapter/trace_evidence_adapter_report.json`
- `reports/trace_evidence_adapter/TRACE_Style_Postcondition_Evidence.md`

## Inputs

Example input:

- `examples/trace_runtime_evidence_examples.json`

Each row includes:

- evidence ID
- action ID
- attestation class
- evidence depth
- runtime class
- workload class
- policy context reference
- observed controls
- execution status

Unsafe rows are skipped when they include prohibited raw evidence fields such as:

- raw attestation
- attestation document
- quote
- secrets
- credentials
- tokens
- raw logs
- payloads

## Output

The adapter normalizes accepted rows into the same observation shape used by `reference_engine.postcondition_evidence`.

That means TRACE-style evidence can feed the same question:

```text
Did the required route controls actually happen after the SMERC decision?
```

## Evidence Boundary

This is a metadata-only TRACE-style adapter stub. It does not implement TRACE, verify hardware attestation, validate TPM or TEE quotes, inspect raw attestations, process secrets, connect to a runtime, prove Linux Foundation endorsement, prove TRACE compatibility, or establish production integrity.

## Why This Matters

TRACE-style evidence is useful to SMERC because recoverability decisions become stronger when postcondition evidence can be bound to a runtime, workload, policy context, and execution outcome.

SMERC should treat attestation as stronger evidence input, not as a replacement for recoverability judgment.

## Work / Result / Impact

Work:

Normalize TRACE-style runtime evidence metadata into SMERC postcondition observations.

Result:

SMERC has a runnable adapter stub showing how future attested-runtime evidence could strengthen postcondition checks while keeping raw attestation material and secrets out of the repository.

Impact:

Reviewers can see how SMERC would benefit from Linux Foundation-adjacent runtime evidence standards without SMERC claiming standards approval or production attestation support.
