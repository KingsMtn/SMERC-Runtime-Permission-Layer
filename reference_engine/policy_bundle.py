from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional

from reference_engine.policy import RuntimePolicy, canonical_json, load_policy
from reference_engine.spl import compile_spl_file


BUNDLE_VERSION = "smerc.policy-bundle.v1"
BUNDLE_SIGNATURE_VERSION = "smerc.policy-bundle-signature.v1"
ARTIFACT_TYPES = {"spl", "runtime_policy", "domain_profile", "control_mapping", "evidence_program"}


def file_sha256(path: str | Path) -> str:
    data = Path(path).read_bytes()
    if b"\0" not in data:
        # Policy artifacts are text; normalize checkout-specific line endings before binding them.
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def bundle_digest(bundle: Mapping[str, Any]) -> str:
    material = {key: value for key, value in dict(bundle).items() if key not in {"bundle_digest", "signature", "verification"}}
    return hashlib.sha256(canonical_json(material).encode("utf-8")).hexdigest()


def build_policy_bundle(
    *,
    bundle_id: str,
    tenant_id: str,
    spl_path: str | Path,
    runtime_policy_path: Optional[str | Path] = None,
    artifact_paths: Iterable[Mapping[str, Any]] = (),
    approved_by: str,
    approved_at: str,
    change_ticket: str,
    environment: str = "pilot-shadow-mode",
    generated_at: Optional[str] = None,
) -> Dict[str, Any]:
    spl_file = Path(spl_path)
    compiled = compile_spl_file(spl_file)
    runtime_policy = load_policy(runtime_policy_path) if runtime_policy_path else compiled
    if runtime_policy.to_dict() != compiled.to_dict():
        raise ValueError("runtime_policy_path does not match compiled SPL output")
    if tenant_id != runtime_policy.tenant_id:
        raise ValueError("tenant_id must match the compiled policy tenant_id")
    _timestamp(approved_at, "approved_at")

    artifacts = [
        _artifact("spl", spl_file),
    ]
    if runtime_policy_path:
        artifacts.append(_artifact("runtime_policy", Path(runtime_policy_path)))
    artifacts.extend(_extra_artifact(item) for item in artifact_paths)

    bundle = {
        "version": BUNDLE_VERSION,
        "bundle_id": _identifier(bundle_id, "bundle_id"),
        "tenant_id": _identifier(tenant_id, "tenant_id", allow_wildcard=True),
        "environment": _text(environment, "environment", 128),
        "generated_at": generated_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "policy": {
            "policy_id": runtime_policy.policy_id,
            "policy_revision": runtime_policy.policy_revision,
            "policy_hash": runtime_policy.policy_hash,
            "mode": runtime_policy.mode,
            "evidence_program_id": runtime_policy.evidence_program_id,
            "evidence_ceiling": runtime_policy.evidence_ceiling,
            "fail_behavior": runtime_policy.fail_behavior,
            "effective_at": runtime_policy.effective_at,
        },
        "approval": {
            "approved_by": _text(approved_by, "approved_by", 128),
            "approved_at": approved_at,
            "change_ticket": _identifier(change_ticket, "change_ticket", maximum=128),
            "activation_gate": "policy bundle must verify before runtime activation",
        },
        "artifacts": artifacts,
        "activation_requirements": [
            "compiled SPL must match the runtime policy hash",
            "bundle signature must verify with the configured key",
            "policy effective_at must be reached before activation",
            "ENFORCE mode requires fail_closed behavior and an enforceable evidence ceiling",
            "changed bundle artifacts require a new approval record",
        ],
        "boundary": {
            "claims": [
                "binds policy identity, hashes, approval metadata, and reviewed artifacts into a replayable bundle",
                "detects accidental or unauthorized bundle drift when verified with a signing key",
                "supports pilot operator review before runtime activation",
            ],
            "limits": [
                "does not replace enterprise change-management approval systems",
                "does not prove that reviewers evaluated the policy correctly",
                "does not provide hardware-backed signing or certificate authority trust",
                "does not claim OPA bundle parity",
            ],
        },
    }
    bundle["bundle_digest"] = bundle_digest(bundle)
    bundle["verification"] = verify_policy_bundle(bundle)
    return bundle


def sign_policy_bundle(bundle: Mapping[str, Any], signing_key: str, *, key_id: str = "local-policy-bundle-key") -> Dict[str, Any]:
    if not isinstance(signing_key, str) or len(signing_key) < 16:
        raise ValueError("signing_key must be a string of at least 16 characters")
    signed = {key: value for key, value in dict(bundle).items() if key not in {"signature", "verification"}}
    digest = bundle_digest(signed)
    signed["bundle_digest"] = digest
    signed["signature"] = {
        "version": BUNDLE_SIGNATURE_VERSION,
        "algorithm": "HMAC-SHA256",
        "key_id": _identifier(key_id, "key_id", maximum=128),
        "bundle_digest": digest,
        "signature": hmac.new(signing_key.encode("utf-8"), digest.encode("ascii"), hashlib.sha256).hexdigest(),
    }
    signed["verification"] = verify_policy_bundle(signed, signing_key=signing_key)
    return signed


def verify_policy_bundle(
    bundle: Mapping[str, Any],
    *,
    signing_key: Optional[str] = None,
    root: str | Path = ".",
) -> Dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(bundle, dict):
        return {"valid": False, "errors": ["bundle must be an object"], "warnings": []}
    if bundle.get("version") != BUNDLE_VERSION:
        errors.append("invalid bundle version")
    expected_digest = bundle_digest(bundle)
    if not hmac.compare_digest(str(bundle.get("bundle_digest", "")), expected_digest):
        errors.append("bundle digest mismatch")
    _verify_required_shape(bundle, errors)
    _verify_artifacts(bundle, Path(root), errors)
    _verify_policy_activation(bundle, errors, warnings)
    signature = bundle.get("signature")
    if signing_key is not None:
        _verify_signature(signature, expected_digest, signing_key, errors)
    elif signature is None:
        warnings.append("bundle is unsigned")
    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "digest_checked": True,
        "signature_checked": signing_key is not None,
    }


def write_policy_bundle_outputs(
    bundle: Mapping[str, Any],
    *,
    json_path: str | Path = "reports/policy_bundle_manifest.json",
    markdown_path: str | Path = "reports/Policy_Bundle_Manifest.md",
) -> None:
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(json_path).write_text(json.dumps(bundle, indent=2, sort_keys=True), encoding="utf-8")
    Path(markdown_path).parent.mkdir(parents=True, exist_ok=True)
    Path(markdown_path).write_text(render_policy_bundle_markdown(bundle), encoding="utf-8")


def render_policy_bundle_markdown(bundle: Mapping[str, Any]) -> str:
    policy = bundle["policy"]
    approval = bundle["approval"]
    verification = bundle.get("verification", {})
    artifacts = bundle.get("artifacts", [])
    lines = [
        "# SMERC Policy Bundle Manifest",
        "",
        f"- Bundle: `{bundle['bundle_id']}`",
        f"- Tenant: `{bundle['tenant_id']}`",
        f"- Environment: `{bundle['environment']}`",
        f"- Policy: `{policy['policy_id']}@{policy['policy_revision']}`",
        f"- Mode: `{policy['mode']}`",
        f"- Evidence ceiling: `{policy['evidence_ceiling']}`",
        f"- Fail behavior: `{policy['fail_behavior']}`",
        f"- Policy hash: `{policy['policy_hash']}`",
        f"- Bundle digest: `{bundle['bundle_digest']}`",
        f"- Verification valid: `{str(verification.get('valid')).lower()}`",
        "",
        "## Approval",
        "",
        f"- Approved by: `{approval['approved_by']}`",
        f"- Approved at: `{approval['approved_at']}`",
        f"- Change ticket: `{approval['change_ticket']}`",
        f"- Activation gate: {approval['activation_gate']}",
        "",
        "## Artifacts",
        "",
        "| Type | Path | SHA-256 |",
        "| --- | --- | --- |",
    ]
    lines.extend(f"| `{item['type']}` | `{item['path']}` | `{item['sha256']}` |" for item in artifacts)
    lines.extend(
        [
            "",
            "## Activation Requirements",
            "",
            *[f"- {item}" for item in bundle.get("activation_requirements", [])],
            "",
            "## Evidence Boundary",
            "",
            "This manifest binds the reviewed policy bundle for replay and operator inspection. It does not replace customer change-management, legal approval, production certification, or OPA/Rego bundle semantics.",
            "",
        ]
    )
    return "\n".join(lines)


def _artifact(kind: str, path: Path) -> Dict[str, Any]:
    if kind not in ARTIFACT_TYPES:
        raise ValueError(f"artifact type must be one of: {', '.join(sorted(ARTIFACT_TYPES))}")
    if not path.is_file():
        raise ValueError(f"artifact path does not exist: {path}")
    return {"type": kind, "path": str(path).replace("\\", "/"), "sha256": file_sha256(path)}


def _extra_artifact(payload: Mapping[str, Any]) -> Dict[str, Any]:
    if set(payload) != {"type", "path"}:
        raise ValueError("artifact entries must contain only type and path")
    return _artifact(str(payload["type"]), Path(str(payload["path"])))


def _verify_required_shape(bundle: Mapping[str, Any], errors: list[str]) -> None:
    required = {
        "version", "bundle_id", "tenant_id", "environment", "generated_at", "policy", "approval",
        "artifacts", "activation_requirements", "boundary", "bundle_digest",
    }
    allowed = required | {"signature", "verification"}
    missing = sorted(required - set(bundle))
    unknown = sorted(set(bundle) - allowed)
    if missing:
        errors.append(f"bundle missing field(s): {', '.join(missing)}")
    if unknown:
        errors.append(f"bundle contains unknown field(s): {', '.join(unknown)}")


def _verify_artifacts(bundle: Mapping[str, Any], root: Path, errors: list[str]) -> None:
    artifacts = bundle.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        errors.append("artifacts must be a non-empty list")
        return
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict) or set(artifact) != {"type", "path", "sha256"}:
            errors.append(f"artifact {index} has invalid shape")
            continue
        if artifact["type"] not in ARTIFACT_TYPES:
            errors.append(f"artifact {index} has unsupported type")
        path = root / str(artifact["path"])
        if not path.is_file():
            errors.append(f"artifact {index} path is not readable")
            continue
        if artifact["sha256"] != file_sha256(path):
            errors.append(f"artifact {index} digest mismatch")


def _verify_policy_activation(bundle: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    policy = bundle.get("policy")
    if not isinstance(policy, dict):
        errors.append("policy must be an object")
        return
    try:
        runtime = RuntimePolicy.from_dict({
            "version": "smerc.policy.v1",
            "tenant_id": bundle.get("tenant_id"),
            "policy_id": policy.get("policy_id"),
            "policy_revision": policy.get("policy_revision"),
            "mode": policy.get("mode"),
            "evidence_program_id": policy.get("evidence_program_id"),
            "evidence_ceiling": policy.get("evidence_ceiling"),
            "fail_behavior": policy.get("fail_behavior"),
            "approved_by_role": bundle.get("approval", {}).get("approved_by", "unknown"),
            "effective_at": policy.get("effective_at"),
            "thresholds": _thresholds_from_embedded_policy(policy),
        })
        if policy.get("policy_hash") and policy.get("policy_hash") != runtime.policy_hash:
            warnings.append("embedded policy hash cannot be fully recalculated without thresholds artifact")
    except Exception as exc:  # strict validation converts to verifier output
        errors.append(str(exc))


def _thresholds_from_embedded_policy(policy: Mapping[str, Any]) -> Dict[str, float]:
    return {
        "deny_exposure_min": 0.78,
        "deny_capacity_max": 0.42,
        "deny_confidence_max": 0.48,
        "deny_cancel_reliability_max": 0.30,
        "deny_cancel_exposure_min": 0.62,
        "escalate_stress_min": 0.70,
        "freeze_confidence_max": 0.45,
        "freeze_capacity_max": 0.36,
        "throttle_authorization_min": 0.62,
        "throttle_exposure_min": 0.45,
    }


def _verify_signature(signature: Any, digest: str, signing_key: str, errors: list[str]) -> None:
    if not isinstance(signature, dict):
        errors.append("missing signature")
        return
    required = {"version", "algorithm", "key_id", "bundle_digest", "signature"}
    missing = sorted(required - set(signature))
    unknown = sorted(set(signature) - required)
    if missing:
        errors.append(f"signature missing field(s): {', '.join(missing)}")
    if unknown:
        errors.append(f"signature contains unknown field(s): {', '.join(unknown)}")
    if signature.get("version") != BUNDLE_SIGNATURE_VERSION:
        errors.append("invalid signature version")
    if signature.get("algorithm") != "HMAC-SHA256":
        errors.append("invalid signature algorithm")
    if not hmac.compare_digest(str(signature.get("bundle_digest", "")), digest):
        errors.append("signature digest mismatch")
    expected = hmac.new(signing_key.encode("utf-8"), digest.encode("ascii"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(str(signature.get("signature", "")), expected):
        errors.append("signature mismatch")


def _identifier(value: Any, path: str, maximum: int = 128, *, allow_wildcard: bool = False) -> str:
    value = _text(value, path, maximum)
    if allow_wildcard and value == "*":
        return value
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,%d}" % (maximum - 1), value):
        raise ValueError(f"{path} must be a safe identifier")
    return value


def _text(value: Any, path: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    value = value.strip()
    if len(value) > maximum:
        raise ValueError(f"{path} must be at most {maximum} characters")
    return value


def _timestamp(value: Any, path: str) -> str:
    value = _text(value, path, 64)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{path} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{path} must include a timezone")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="Build or verify a SMERC policy bundle manifest.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build")
    build.add_argument("--bundle-id", default="github-actions-shadow-mode-2026-07-07")
    build.add_argument("--tenant-id", default="platform-team")
    build.add_argument("--spl", type=Path, default=Path("examples/policies/github_actions_shadow_spl.json"))
    build.add_argument("--artifact", action="append", default=[], help="Additional artifact in type=path form")
    build.add_argument("--approved-by", default="security-architecture-review")
    build.add_argument("--approved-at", default="2026-07-07T00:00:00Z")
    build.add_argument("--change-ticket", default="SMERC-PILOT-001")
    build.add_argument("--signing-key")
    build.add_argument("--key-id", default="local-policy-bundle-key")
    build.add_argument("--json-out", type=Path, default=Path("reports/policy_bundle_manifest.json"))
    build.add_argument("--markdown-out", type=Path, default=Path("reports/Policy_Bundle_Manifest.md"))

    verify = subparsers.add_parser("verify")
    verify.add_argument("bundle", type=Path)
    verify.add_argument("--signing-key")

    args = parser.parse_args()
    if args.command == "build":
        extras = []
        for item in args.artifact:
            if "=" not in item:
                raise ValueError("--artifact must be in type=path form")
            kind, path = item.split("=", 1)
            extras.append({"type": kind, "path": path})
        bundle = build_policy_bundle(
            bundle_id=args.bundle_id,
            tenant_id=args.tenant_id,
            spl_path=args.spl,
            artifact_paths=extras,
            approved_by=args.approved_by,
            approved_at=args.approved_at,
            change_ticket=args.change_ticket,
        )
        if args.signing_key:
            bundle = sign_policy_bundle(bundle, args.signing_key, key_id=args.key_id)
        write_policy_bundle_outputs(bundle, json_path=args.json_out, markdown_path=args.markdown_out)
        print(json.dumps(bundle, indent=2, sort_keys=True))
    else:
        bundle = json.loads(args.bundle.read_text(encoding="utf-8"))
        print(json.dumps(verify_policy_bundle(bundle, signing_key=args.signing_key), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
