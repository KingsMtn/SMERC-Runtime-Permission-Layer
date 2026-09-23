# SMERC Portable Evidence Contract v1

`smerc.portable-evidence.v1` is a normalized, bounded record for exchanging SMERC execution evidence across GitHub, AWS, MCP, and offline review tools.

It answers:

- what workload and model identity were reported
- which repository, commit, workflow, and ephemeral ref produced the run
- where it executed and under which principal
- which policy bundle and enforcement mode governed it
- whether admission succeeded and which posture was returned
- which tools were called, represented by bounded names and a transcript digest
- whether failure was contained and cleanup was verified
- which data classes were touched and which fields were redacted

## Verification levels

`sha256` proves deterministic record integrity only. It does not authenticate the issuer.

`hmac_sha256` authenticates the record to a verifier that already possesses the shared verification key. The key is never included in the record. This reference method is suitable for controlled pilots, but it is not a public-key signature or independent hardware attestation.

Both modes reject unknown fields, modified payloads, inconsistent cleanup claims, and records that claim secrets were persisted.

## TRACE relationship

The field selection is informed by the public TRACE questions: what ran, where it ran, under which policy, which data it touched, and which tools it called. SMERC does not claim TRACE compatibility or conformance. TRACE remains a developer-preview specification, and SMERC v1 does not provide a TEE measurement, trusted-root attestation, SCITT receipt, or public-key signature.

Future interoperability work should use an explicit adapter and conformance fixtures rather than silently treating similarly named fields as equivalent.

## Runner lifecycle

For an ephemeral GitHub/AWS runner, `source_control.ephemeral_ref`, `runtime.execution_boundary`, `containment.failure_contained`, `containment.cleanup_status`, and `containment.cleanup_verified` must be populated from observed platform evidence. A requested cleanup is not a verified cleanup.

The contract does not authorize execution. SMERC admission, IAM, GitHub permissions, and the target platform remain the enforcement boundaries.
