# SMERC Customer Proof Loop Report

Generated: `2026-09-15T21:55:53+00:00`
Tenant: `openssf-issue-50-probe`

## Result

- Overall status: **REVIEW**
- Runtime admission: **ADMIT**
- Recoverability posture: **FREEZE**
- SPARTa route: **PAUSE**
- Ledger valid: **True**

## Pass/Fail Checks

| Check | Result |
| --- | --- |
| Hard runtime gates passed | `True` |
| Recoverability permits progression | `False` |
| Route executable | `False` |
| Ledger valid | `True` |

## Reason Codes

- `EVIDENCE_VALIDITY_UNAVAILABLE`
- `EXTERNAL_SIDE_EFFECT`
- `IRREVERSIBLE_EXPOSURE_ELEVATED`
- `RECOVERABILITY_EVIDENCE_UNAVAILABLE`
- `ROLLBACK_LATENCY_UNAVAILABLE`
- `RUNTIME_ADMISSION_ADMIT`
- `SPARTA_FREEZE_PAUSES_AUTOMATION`

## Controls

- `checkpoint_before_execution`
- `collect_more_evidence`
- `continue_to_recoverability_scoring`
- `pause_execution`
- `preserve_replay`
- `snapshot_current_state`
- `treat_unavailable_recoverability_as_uncertainty`

## Plain English

Runtime admission returned ADMIT. SMERC posture is FREEZE. SPARTa route is PAUSE. The lifecycle ledger is valid: True.

## Evidence Artifacts

- Full JSON evidence bundle: `customer_proof_loop.json`
- Replayable lifecycle chain: `decision_lifecycle_ledger` inside the JSON bundle
