# SMERC Runtime Contract Index

The Runtime Contract Index is the assembly map for SMERC.

Contract version: `smerc.runtime-contract-index.v1`.

SMERC now has many working contracts: action language, decision language, policy, SPL, SPARTa route, SPARTa vocabulary, permits, control evidence, execution reports, Decision Lifecycle Ledger, DLL Intelligence, and certificates.

It also has proposed adjacent contract directions for SPARK signal intake and timing evidence. These are documented as architecture direction, not production schemas.

The index answers the practical reviewer question:

> How do these pieces fit together as one runtime governance system?

## Canonical Files

- Specification: `specification/SMERC_Runtime_Contract_Index_v1.md`
- Schema: `schemas/smerc-runtime-contract-index-v1.schema.json`
- Example: `examples/runtime_contract_index.json`

## Why This Matters

Without an index, an outside AI agent, integration partner, or CISO reviewer has to infer the system from many separate docs.

With the index, the system becomes:

```text
discover -> collect signals -> declare action -> decide posture -> route with SPARTa -> enforce or review -> collect evidence -> record DLL -> measure timing -> analyze DLL
```

## Boundary

The index is a map. It does not certify production readiness, prove customer outcomes, or replace security review.
