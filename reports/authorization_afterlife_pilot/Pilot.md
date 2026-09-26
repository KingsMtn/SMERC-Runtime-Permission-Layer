# Authorization-Afterlife Pilot Decisions

- Pilot: `aws-afterlife-metadata-pilot`
- Records: `3`
- Decisions: `{'SETTLE': 1, 'QUARANTINE': 1, 'COMPENSATE': 1, 'DENY': 0}`

## Decision Records

### aws-read-settlement-001

- Evidence class: `CONTROLLED_AWS_PROOF`
- Action: `aws-read-summary` / `read`
- Decision: `SETTLE`
- Should commit: `true`
- Reasons: none
- Required actions: none

### aws-epoch-drift-002

- Evidence class: `SYNTHETIC`
- Action: `aws-policy-drift-read` / `read`
- Decision: `QUARANTINE`
- Should commit: `false`
- Reasons: acquired:authority_epoch_changed, continuing:authority_epoch_changed
- Required actions: hold_commit, revalidate_authority_and_evidence

### aws-revoked-partial-002

- Evidence class: `SYNTHETIC`
- Action: `aws-ephemeral-mutation` / `create_ephemeral`
- Decision: `COMPENSATE`
- Should commit: `false`
- Reasons: acquired:authority_epoch_changed, continuing:contract_revoked, continuing:authority_epoch_changed, continuing:partial_effects_require_compensation
- Required actions: execute_compensation, verify_cleanup_before_settlement

## Evidence Boundary

Decisions are deterministic evaluations of supplied, validated metadata. SMERC preserves the declared evidence class and source digest but does not verify upstream truth, AWS attestation, customer production safety, or complete transport enforcement.
