# Authorization-Afterlife Evidence Intake

- Pilot: `aws-afterlife-metadata-pilot`
- Records: `2`
- Reconciliation required: `1`
- Readiness: `ready_for_scenario_reconciliation`

## Records

| Evidence | Class | Authority changed | Settlement evidence | Reconcile |
|---|---|---:|---:|---:|
| `aws-read-settlement-001` | `CONTROLLED_AWS_PROOF` | `false` | `true` | `false` |
| `aws-revoked-partial-002` | `SYNTHETIC` | `true` | `true` | `true` |

## Evidence Boundary

This intake validates metadata shape, provenance declarations, and the non-secret boundary. It does not verify source truth, AWS attestation, customer production safety, or authority itself.
