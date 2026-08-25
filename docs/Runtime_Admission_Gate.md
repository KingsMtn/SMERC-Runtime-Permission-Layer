# Runtime Admission Gate

SMERC now separates deterministic admission from recoverability scoring.

The runtime order is:

```text
request
-> runtime admission gate
-> SMERC recoverability scoring
-> SPARTa route
-> Decision Lifecycle Ledger evidence
```

The admission gate answers one narrow question:

> Are the action facts trusted enough to score?

## Required Checks

The reference gate can evaluate:

- `identity_valid`
- `session_scope_valid`
- `permit_valid`
- `typed_contract_valid`
- `attestation_valid`
- `least_privilege_confirmed`
- `object_shape_expected`
- `required_evidence_present`

Each pilot can declare which checks are required. Required failures produce `REJECT`; optional failures produce `ESCALATE`.

## Outputs

`reference_engine.runtime_admission_gate` returns:

- `ADMIT`
- `REJECT`
- `ESCALATE`

It also returns a maximum recommended posture. A rejected request is capped at `DENY` before recoverability scoring can influence execution.

## Why This Matters

Recoverability is not a substitute for authority, typed contracts, attestation, least privilege, payload validation, or evidence admission.

A malformed or unauthorized action can be reversible and still fail. SMERC should not rescue it. The runtime admission gate makes that rule explicit in code.

## Boundary

This module does not authenticate remote systems by itself and does not replace IAM, OPA, API gateways, endpoint schemas, MCP implementations, or customer-specific policy. It is a deterministic pre-scoring contract that lets adapters prove which hard facts were present before recoverability scoring ran.
