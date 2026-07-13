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

## Cross-Checks

| Check | Result | Detail |
| --- | --- | --- |
| `decision_posture_matches_route_source` | `pass` | decision posture THROTTLE vs route source THROTTLE |
| `decision_replay_matches_route` | `pass` | decision replay replay_example_throttle_001 vs route replay replay_example_throttle_001 |
| `route_controls_are_mapped_or_not_required` | `pass` | route controls should be explainable by the control mapping library or documented as route-level controls |
| `control_mapping_has_no_missing_required_controls` | `pass` | control mapping should not hide missing native mechanisms |
| `ledger_hash_chain_valid` | `pass` | decision lifecycle ledger must verify before being used as evidence |

## Artifacts

| Artifact | Version | Digest |
| --- | --- | --- |
| `decision`: `examples/sparta/throttle_decision.json` | `unversioned` | `67489df69df74b81b92d7b31222e93789d814b0d4492eb8b97a62b4bfde58871` |
| `route_report`: `reports/signed_sparta_route_example.json` | `smerc.sparta-route.v1` | `385b45c38646960770c8949c3cc755dac9781967755f63c3e589ae518201a923` |
| `control_mapping_report`: `reports/control_mapping_example.json` | `smerc.control-mapping-report.v1` | `837a816ab187d9045584facf143ee56a8cf4f45684575e57905b9ae7347571e9` |
| `decision_lifecycle_ledger`: `reports/decision_lifecycle_ledger_example.json` | `smerc.decision-lifecycle-ledger.v1` | `f1c06132003d4fe32fe21c4c7980da703df7d815b00a1c78d50e1e20cd5b9c30` |

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

SMERC returned THROTTLE; SPARTa routed it to CONSTRAINED_EXECUTE; control mapping executable is true; 0 cross-check(s) failed.
