# Ephemeral Execution Envelopes

SMERC Ephemeral Execution Envelopes provide a containment boundary for code-writing
agents. Each run is bound to an immutable base commit, an isolated ephemeral ref,
a SMERC permit and replay, an exact execution-target digest, a policy digest, and a
short expiration window.

The lifecycle is `CREATED -> ACTIVE -> SEALED -> PROMOTED`. An envelope may instead
become `DISCARDED` or `EXPIRED`. Terminal envelopes cannot return to execution.
Direct writes to durable refs are prohibited. Promotion requires successful tests,
accountable review approval, a fresh policy check, verified isolation, the exact
approved target digest, a sealed commit digest, and a non-ephemeral destination ref.

This module defines and verifies the contract. It does not itself create Git branches,
delete refs, or bypass repository protection rules. A GitHub or Git adapter must enforce
the verified envelope and retain the terminal manifest after branch cleanup.

## TRACE export boundary

`reference_engine.trace_evidence_export` maps a verified envelope into an unsigned
TRACE v0.2-shaped export candidate. The output is deliberately labeled `unverified`,
`signed: false`, and `hardware_attested: false`. It must not be represented as a TRACE
Trust Record until an independent implementation adds schema validation, trusted key
management, signing, freshness and revocation checks, and any required attestation or
transparency-log verification.

TRACE references are used under their published licenses. See `THIRD_PARTY_NOTICES.md`.
