# SMERC Policy Bundle Manifest

- Bundle: `github-actions-shadow-mode-2026-07-07`
- Tenant: `platform-team`
- Environment: `pilot-shadow-mode`
- Policy: `github-actions-shadow-mode@2026.07.07`
- Mode: `OBSERVE`
- Evidence ceiling: `OBSERVE`
- Fail behavior: `report_unavailable`
- Policy hash: `cc7b8bfd3d8f87eb10158bba6b203d5691de16529dc289a840fd7c2e0417f886`
- Bundle digest: `d7ff0961fe53f3507479c343d27a1ffa67309563bfeb85d858048755f2dae3b5`
- Verification valid: `true`

## Approval

- Approved by: `security-architecture-review`
- Approved at: `2026-07-07T00:00:00Z`
- Change ticket: `SMERC-PILOT-001`
- Activation gate: policy bundle must verify before runtime activation

## Artifacts

| Type | Path | SHA-256 |
| --- | --- | --- |
| `spl` | `examples/policies/github_actions_shadow_spl.json` | `3ba496421c32ab97c1d6bb70cf882085337922bf86a7f9914a8eea9c32eea044` |
| `domain_profile` | `examples/domain_profiles/github_actions_strict.json` | `f0cc1986dad6fd0282cad0fe6c0a4e16aef27f79203e5498ae1d053cf08a8c44` |
| `control_mapping` | `examples/control_mapping/github_actions_controls.json` | `b8816613a573cd6d95a7fcc95df4768cd6996dd9827380558a3e9fd03b262650` |

## Activation Requirements

- compiled SPL must match the runtime policy hash
- bundle signature must verify with the configured key
- policy effective_at must be reached before activation
- ENFORCE mode requires fail_closed behavior and an enforceable evidence ceiling
- changed bundle artifacts require a new approval record

## Evidence Boundary

This manifest binds the reviewed policy bundle for replay and operator inspection. It does not replace customer change-management, legal approval, production certification, or OPA/Rego bundle semantics.
