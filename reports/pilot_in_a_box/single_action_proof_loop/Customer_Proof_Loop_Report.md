# SMERC Customer Proof Loop Report

Generated: `2026-08-29T00:19:23+00:00`
Tenant: `customer-proof-demo`

## Result

- Overall status: **PASS**
- Runtime admission: **ADMIT**
- Recoverability posture: **THROTTLE**
- SPARTa route: **CONSTRAINED_EXECUTE**
- Ledger valid: **True**

## Pass/Fail Checks

| Check | Result |
| --- | --- |
| Hard runtime gates passed | `True` |
| Recoverability permits progression | `True` |
| Route executable | `True` |
| Ledger valid | `True` |

## Reason Codes

- `EXTERNAL_SIDE_EFFECT`
- `IRREVERSIBLE_EXPOSURE_ELEVATED`
- `RUNTIME_ADMISSION_ADMIT`
- `SPARTA_THROTTLE_WITH_NATIVE_CONTROLS`

## Controls

- `checkpoint_before_execution`
- `continue_to_recoverability_scoring`
- `limit_scope`
- `preserve_replay`
- `preview_before_execution`
- `rate_limit_external_side_effect`
- `record_execution_report`
- `record_replay`
- `require_rollback_plan`

## Plain English

Runtime admission returned ADMIT. SMERC posture is THROTTLE. SPARTa route is CONSTRAINED_EXECUTE. The lifecycle ledger is valid: True.

## Evidence Artifacts

- Full JSON evidence bundle: `customer_proof_loop.json`
- Replayable lifecycle chain: `decision_lifecycle_ledger` inside the JSON bundle
