# SMERC Policy Bundle Manifest

- Bundle: `github-actions-shadow-mode-2026-07-07`
- Tenant: `platform-team`
- Environment: `pilot-shadow-mode`
- Policy: `github-actions-shadow-mode@2026.07.07`
- Mode: `OBSERVE`
- Evidence ceiling: `OBSERVE`
- Fail behavior: `report_unavailable`
- Policy hash: `cc7b8bfd3d8f87eb10158bba6b203d5691de16529dc289a840fd7c2e0417f886`
- Bundle digest: `158e581c4ffe0fdcf3221d3a10943c7cfb5078e4b0207343652a41d8f99fbed0`
- Verification valid: `true`

## Approval

- Approved by: `security-architecture-review`
- Approved at: `2026-07-07T00:00:00Z`
- Change ticket: `SMERC-PILOT-001`
- Activation gate: policy bundle must verify before runtime activation

## Artifacts

| Type | Path | SHA-256 |
| --- | --- | --- |
| `spl` | `examples/policies/github_actions_shadow_spl.json` | `75ecc57a1271f313dc0f3a47eafc7616f4644154b9a188bb4fb803308ab83f90` |
| `domain_profile` | `examples/domain_profiles/github_actions_strict.json` | `401601df03294e9274699894364bd3dc755ca2f5807315cb6821042b71ea9940` |
| `control_mapping` | `examples/control_mapping/github_actions_controls.json` | `536b2913df1b13683e28ca553a5095e011403b5dd727a6aab458992077b7c508` |

## Activation Requirements

- compiled SPL must match the runtime policy hash
- bundle signature must verify with the configured key
- policy effective_at must be reached before activation
- ENFORCE mode requires fail_closed behavior and an enforceable evidence ceiling
- changed bundle artifacts require a new approval record

## Evidence Boundary

This manifest binds the reviewed policy bundle for replay and operator inspection. It does not replace customer change-management, legal approval, production certification, or OPA/Rego bundle semantics.
