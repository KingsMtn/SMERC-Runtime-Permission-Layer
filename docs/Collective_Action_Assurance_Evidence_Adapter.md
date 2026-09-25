# Collective Action Assurance Evidence Adapter

## Purpose

Collective Action Assurance (AA) studies whether individually authorized actions combine into an unsafe collective consequence. Runtime Assurance (RA) governs whether a specific action may cross a real execution boundary.

This adapter is the narrow contract between them. It validates smerc.collective-decision-envelope.v1 without copying AA's research engine into RA.

## Runtime Semantics

| AA evidence | RA adapter result | Maximum posture |
| --- | --- | --- |
| Valid and no collective risk observed | ACCEPT_EVIDENCE | No additional posture |
| Valid and collective review advised | ESCALATE | FREEZE |
| Malformed, stale, tampered, out of scope, discontinuous, or false authority claim | REJECT | DENY |

ACCEPT_EVIDENCE never means ALLOW. AA envelopes carry authority_effect: NONE; identity, admission, recoverability, permits, and all other RA controls still apply.

## Validated Bindings

- contract and producer versions;
- exact resource, action, and operation scope;
- issue and expiry time;
- participant normalization and quorum consistency;
- predecessor continuity when required;
- report and envelope digests;
- strict field set; and
- the prohibition against AA granting authority.

The adapter performs no network calls and does not deploy resources. It is a deterministic reference implementation for testing the AA-to-RA boundary.
