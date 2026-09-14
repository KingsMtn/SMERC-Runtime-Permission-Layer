# TRACE-Style Evidence Adapter Report

Generated: `2026-09-14T11:04:49+00:00`
Version: `smerc.trace-evidence-adapter.v0`
Status: `limited_trace_style_review`

## Purpose

This report shows how metadata-only runtime evidence shaped like future TRACE-style attestations can be normalized into SMERC postcondition evidence.

## Work / Result / Impact

- Work: Normalize TRACE-style runtime evidence metadata into SMERC postcondition observations.
- Result: Accepted 3 metadata-only rows, skipped 1 unsafe rows, and produced 3 postcondition observation rows.
- Impact: SMERC can show how attested-runtime-shaped evidence could strengthen postcondition checks without claiming live TRACE compatibility or hardware attestation verification.

## Summary

- Accepted rows: `3`
- Skipped rows: `1`
- Attestation class counts: `{'trace_style_metadata_only': 3}`
- Evidence depth counts: `{'partial_runtime_control_observation': 1, 'runtime_execution_observation': 1, 'runtime_policy_and_control_observation': 1}`

## Evidence Boundary

This is a metadata-only TRACE-style adapter stub. It does not implement TRACE, verify hardware attestation, validate TPM/TEE quotes, inspect raw attestations, process secrets, connect to a runtime, prove Linux Foundation endorsement, prove TRACE compatibility, or establish production integrity.

## Postcondition Summary

- Evaluated actions: `10`
- Observed actions: `3`
- Postcondition status counts: `{'gap': 1, 'pass': 2, 'unobserved': 7}`
- Route control evidence: `{'required_control_count': 30, 'applied_required_control_count': 9, 'missing_required_control_count': 21, 'failed_required_control_count': 0, 'route_control_evidence_ratio': 0.3}`

## Skipped Rows

| Evidence ID | Reason |
| --- | --- |
| `TRACE_STYLE_UNSAFE_RAW_ATTESTATION` | `prohibited field present: evidence.raw_attestation` |

## Reviewer Question

Could a real runtime or attestation service produce signed metadata for these controls without exposing raw attestations, secrets, raw logs, or customer data?
