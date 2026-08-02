# SMERC Policy Bundle Manifest

SMERC policy bundle manifests bind a reviewed SPL policy, compiled runtime policy identity, domain profile, control mapping, approval metadata, artifact hashes, and an optional signature into one replayable activation record.

This is intended to answer an enterprise operator question:

> Which policy bundle was active, who approved it, what files were reviewed, and did anything drift before the runtime used it?

## What It Adds

- A deterministic bundle digest over the policy activation record.
- File hashes for reviewed artifacts such as SPL, domain profiles, and control mappings.
- Approval metadata including approver role, approval time, change ticket, and activation gate.
- HMAC signing and verification for pilot environments.
- Explicit activation requirements before a policy is used by runtime evaluation.
- Clear evidence boundaries that avoid claiming production certification, OPA bundle parity, or legal change-management approval.

## Command

```powershell
python -m reference_engine.policy_bundle build `
  --signing-key local-policy-bundle-signing-key-012345 `
  --key-id pilot-policy-key-1 `
  --artifact domain_profile=examples/domain_profiles/github_actions_strict.json `
  --artifact control_mapping=examples/control_mapping/github_actions_controls.json
```

Outputs:

- `reports/policy_bundle_manifest.json`
- `reports/Policy_Bundle_Manifest.md`

## Verification

```powershell
python -m reference_engine.policy_bundle verify reports/policy_bundle_manifest.json `
  --signing-key local-policy-bundle-signing-key-012345
```

Verification checks:

- Bundle digest matches the canonical manifest.
- Signature matches the bundle digest when a signing key is supplied.
- Referenced artifact paths exist.
- Referenced artifact hashes still match.
- Embedded policy activation metadata is structurally valid.

## Why This Matters To CISOs

OPA, IAM, and change-management systems train enterprise teams to ask for policy identity, approval trail, versioning, and replay. SMERC should speak that language without pretending to be those systems.

The policy bundle manifest gives SMERC a tighter operational story:

- SMERC evaluates runtime action posture.
- SPL defines the policy thresholds and operating mode.
- The policy bundle records what was approved for use.
- Operator status reports show what is active.
- OPA-style decision logs let existing audit pipelines inspect outcomes.

## Boundary

This is a pilot-grade reference mechanism. It does not replace enterprise CAB approval, production key management, certificate authority trust, legal recordkeeping, or OPA/Rego bundle semantics. Customer production deployments should use their own signing, artifact storage, approval workflow, and retention controls.
