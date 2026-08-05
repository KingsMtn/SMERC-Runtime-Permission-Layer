# SMERC GitHub Actions Governance Report

Audience: CISO, security architect, platform engineering reviewer

This is a replayable pilot governance report. It assembles existing SMERC artifacts and cross-checks them. It is not production certification, compliance attestation, or proof of live incident reduction.

## Scenario

AI-assisted production deployment request where SMERC returns THROTTLE, SPARTa routes to constrained execution, controls map to GitHub Actions mechanisms, and DLL records the governed decision lifecycle.

## Executive Summary

- SMERC posture: `THROTTLE`
- SPARTa route state: `CONSTRAINED_EXECUTE`
- Route executable: `true`
- Control mapping executable: `true`
- Mapped controls: `4`
- Missing controls: `0`
- DLL records: `7`
- DLL valid: `true`
- Evidence artifacts: `4`
- Permit ID: `permit_0123456789abcdef0123456789abcdef`
- Execution outcome: `SUCCEEDED`
- Reviewer verdict: `agree`

## Cross-Checks

| Check | Result | Detail |
| --- | --- | --- |
| `decision_posture_matches_route_source` | `pass` | decision posture THROTTLE vs route source THROTTLE |
| `decision_replay_matches_route` | `pass` | decision replay replay_example_throttle_001 vs route replay replay_example_throttle_001 |
| `route_controls_are_mapped_or_not_required` | `pass` | route controls should be explainable by the control mapping library or documented as route-level controls |
| `control_mapping_has_no_missing_required_controls` | `pass` | control mapping should not hide missing native mechanisms |
| `ledger_hash_chain_valid` | `pass` | decision lifecycle ledger must verify before being used as evidence |
| `permit_replay_matches_decision` | `pass` | permit replay replay_example_throttle_001 vs decision replay replay_example_throttle_001 |
| `permit_controls_are_route_controls` | `pass` | permit required controls should be a subset of SPARTa applied controls |
| `control_evidence_satisfies_permit` | `pass` | control evidence should show each permit-required control was observed |
| `execution_consumed_same_permit` | `pass` | execution permit permit_0123456789abcdef0123456789abcdef vs permit permit_0123456789abcdef0123456789abcdef |
| `execution_sparta_route_matches_route_report` | `pass` | execution report SPARTa evidence should bind to the supplied route report |
| `reviewer_outcome_matches_decision` | `pass` | reviewer outcome replay replay_example_throttle_001 vs decision replay replay_example_throttle_001 |

## Artifacts

| Artifact | Version | Digest |
| --- | --- | --- |
| `decision`: `examples/sparta/throttle_decision.json` | `unversioned` | `67489df69df74b81b92d7b31222e93789d814b0d4492eb8b97a62b4bfde58871` |
| `route_report`: `reports/signed_sparta_route_example.json` | `smerc.sparta-route.v1` | `385b45c38646960770c8949c3cc755dac9781967755f63c3e589ae518201a923` |
| `control_mapping_report`: `reports/control_mapping_example.json` | `smerc.control-mapping-report.v1` | `837a816ab187d9045584facf143ee56a8cf4f45684575e57905b9ae7347571e9` |
| `decision_lifecycle_ledger`: `reports/decision_lifecycle_ledger_example.json` | `smerc.decision-lifecycle-ledger.v1` | `f1c06132003d4fe32fe21c4c7980da703df7d815b00a1c78d50e1e20cd5b9c30` |
| `control_evidence_report`: `reports/control_evidence_receipt_example.json` | `smerc.control-evidence.v1` | `7ee021c5ef5d2f7201b58d70f667d027529f5a95e71e5b0f79c02ab78548ed1b` |
| `execution_report`: `reports/execution_report_example.json` | `smerc.execution-report.v1` | `8687c347456247e127194e2f4d2bb9c3ed33d37eea2020927a24a27b8c006c18` |
| `permit_report`: `reports/action_bound_permit_example.json` | `smerc.permit.v1` | `9ab55e8a5fa11c8d0b860fba4eff8c3b17933bf224375f6f3298ba234e5d1e09` |
| `reviewer_outcome`: `reports/reviewer_outcome_example.json` | `smerc.reviewer-outcome.v1` | `6c34d1a4b11547809418a0f6d55c88dcec106fd94789c756951c11cc2c01ee68` |

## Review Notes

- Use this report to inspect whether the decision, route, controls, and lifecycle evidence agree.
- Treat the report as pilot evidence for review, not as a claim of production certification.
- Reviewer should confirm the native controls are actually enforced by the target workflow before enabling enforcement mode.

## Known Limits

- The example uses repository artifacts and synthetic pilot evidence.
- The signed SPARTa route uses pilot-grade HMAC signing, not managed production key infrastructure.
- Control mapping declares expected mechanisms; adapter validation is still required.
- The report does not prove live incident reduction or regulatory compliance.

## Recommended Next Action

Use this bundle as pilot review evidence; validate native enforcement and collect external reviewer feedback before production claims.

SMERC returned THROTTLE; SPARTa routed it to CONSTRAINED_EXECUTE; control mapping executable is true; 0 cross-check(s) failed. Permit, control evidence, execution, and reviewer outcome are included when supplied by the bundle.
