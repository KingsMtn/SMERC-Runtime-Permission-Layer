from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.claim_registry import build_claim_registry


VERSION = "smerc.evidence-bundle.v1"

DEFAULT_ARTIFACTS = [
    "reports/Claim_Registry.md",
    "reports/claim_registry.json",
    "reports/End_To_End_Reviewer_Flow.md",
    "reports/Local_Shadow_Intake_Report.md",
    "reports/Public_Fallback_Adapter_Report.md",
    "reports/Public_Evidence_Fallback_Plan.md",
    "docs/End_To_End_Reviewer_Flow.md",
    "docs/Local_Shadow_Intake.md",
    "docs/Public_Fallback_Adapter.md",
    "docs/Public_Evidence_Fallback_Plan.md",
    "docs/Small_Generated_Stress_Corpus.md",
    "examples/smerc_stress_corpus_small.json",
    "reports/Small_Generated_Stress_Corpus_Report.md",
    "reports/small_generated_stress_corpus_report.json",
]

REQUIRED_BUNDLE_FIELDS = {
    "version",
    "generated_at",
    "artifact_count",
    "artifacts",
    "claim_summary",
    "evidence_boundary",
}

REQUIRED_ARTIFACT_FIELDS = {"path", "sha256", "size_bytes", "purpose"}


def build_evidence_bundle(*, root: str | Path = ".", artifact_paths: list[str] | None = None) -> Dict[str, Any]:
    base = Path(root)
    paths = artifact_paths or DEFAULT_ARTIFACTS
    artifacts = [_artifact(base, path) for path in paths]
    registry = build_claim_registry(root=base)
    return {
        "version": VERSION,
        "generated_at": _now(),
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "claim_summary": {
            "claim_count": registry["claim_count"],
            "status_counts": registry["status_counts"],
        },
        "evidence_boundary": (
            "This bundle verifies local artifact presence and SHA-256 digests. It does not prove customer validation, "
            "production safety, incident reduction, AWS endorsement, or official benchmark performance."
        ),
    }


def verify_evidence_bundle(bundle: Mapping[str, Any], *, root: str | Path = ".") -> Dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    base = Path(root)
    _verify_bundle_shape(bundle, errors)
    verified = 0
    if not errors:
        for artifact in bundle["artifacts"]:
            path = base / artifact["path"]
            if not path.exists():
                errors.append(f"missing artifact: {artifact['path']}")
                continue
            actual_size = path.stat().st_size
            actual_hash = _sha256(path)
            if actual_size != artifact["size_bytes"]:
                errors.append(f"size mismatch for {artifact['path']}")
            if actual_hash != artifact["sha256"]:
                errors.append(f"sha256 mismatch for {artifact['path']}")
            if not errors or actual_hash == artifact["sha256"]:
                verified += 1
        if bundle["artifact_count"] != len(bundle["artifacts"]):
            errors.append("artifact_count does not match artifacts length")
        if bundle["claim_summary"]["claim_count"] <= 0:
            errors.append("claim_summary.claim_count must be positive")
    return {
        "valid": not errors,
        "verified_artifact_count": verified,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
    }


def render_markdown(bundle: Mapping[str, Any], verification: Mapping[str, Any] | None = None) -> str:
    lines = [
        "# SMERC Evidence Bundle",
        "",
        f"Generated: `{bundle['generated_at']}`",
        f"Version: `{bundle['version']}`",
        "",
        "## Claim Summary",
        "",
        f"- Claims: `{bundle['claim_summary']['claim_count']}`",
        f"- Status counts: `{bundle['claim_summary']['status_counts']}`",
        "",
        "## Artifacts",
        "",
        "| Path | Size | SHA-256 | Purpose |",
        "| --- | ---: | --- | --- |",
    ]
    for artifact in bundle["artifacts"]:
        lines.append(
            f"| `{artifact['path']}` | {artifact['size_bytes']} | `{artifact['sha256']}` | {artifact['purpose']} |"
        )
    if verification is not None:
        lines.extend(
            [
                "",
                "## Verification",
                "",
                f"- Valid: `{verification['valid']}`",
                f"- Verified artifacts: `{verification['verified_artifact_count']}`",
                f"- Errors: `{verification['errors']}`",
                f"- Warnings: `{verification['warnings']}`",
            ]
        )
    lines.extend(["", "## Evidence Boundary", "", str(bundle["evidence_boundary"]), ""])
    return "\n".join(lines)


def write_outputs(
    bundle: Mapping[str, Any],
    *,
    json_output: str | Path = "reports/evidence_bundle.json",
    markdown_output: str | Path = "reports/Evidence_Bundle.md",
    root: str | Path = ".",
) -> Dict[str, Any]:
    verification = verify_evidence_bundle(bundle, root=root)
    Path(json_output).parent.mkdir(parents=True, exist_ok=True)
    Path(markdown_output).parent.mkdir(parents=True, exist_ok=True)
    Path(json_output).write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(markdown_output).write_text(render_markdown(bundle, verification), encoding="utf-8")
    return verification


def load_bundle(path: str | Path) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("evidence bundle must be a JSON object")
    return payload


def _artifact(root: Path, path: str) -> Dict[str, Any]:
    full = root / path
    if not full.exists():
        raise FileNotFoundError(f"bundle artifact does not exist: {path}")
    return {
        "path": path,
        "sha256": _sha256(full),
        "size_bytes": full.stat().st_size,
        "purpose": _purpose(path),
    }


def _verify_bundle_shape(bundle: Mapping[str, Any], errors: list[str]) -> None:
    missing = sorted(REQUIRED_BUNDLE_FIELDS - set(bundle))
    unknown = sorted(set(bundle) - REQUIRED_BUNDLE_FIELDS)
    if missing:
        errors.append(f"bundle missing fields: {', '.join(missing)}")
    if unknown:
        errors.append(f"bundle contains unknown fields: {', '.join(unknown)}")
    artifacts = bundle.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        errors.append("artifacts must be a non-empty list")
        return
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict):
            errors.append(f"artifact {index} must be an object")
            continue
        missing_artifact = sorted(REQUIRED_ARTIFACT_FIELDS - set(artifact))
        unknown_artifact = sorted(set(artifact) - REQUIRED_ARTIFACT_FIELDS)
        if missing_artifact:
            errors.append(f"artifact {index} missing fields: {', '.join(missing_artifact)}")
        if unknown_artifact:
            errors.append(f"artifact {index} contains unknown fields: {', '.join(unknown_artifact)}")


def _purpose(path: str) -> str:
    if "Claim" in path or "claim_registry" in path:
        return "claim status and boundaries"
    if "End_To_End" in path:
        return "end-to-end reviewer flow evidence"
    if "Local_Shadow" in path:
        return "reject-first metadata intake evidence"
    if "Public_Fallback" in path:
        return "public-pattern fallback adapter evidence"
    if "Public_Evidence_Fallback" in path:
        return "public evidence fallback provenance"
    return "supporting evidence artifact"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build or verify a SMERC evidence bundle.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build")
    build.add_argument("--root", default=".")
    build.add_argument("--json-output", default="reports/evidence_bundle.json")
    build.add_argument("--markdown-output", default="reports/Evidence_Bundle.md")
    build.add_argument("--pretty", action="store_true")
    verify = subparsers.add_parser("verify")
    verify.add_argument("bundle")
    verify.add_argument("--root", default=".")
    args = parser.parse_args()
    if args.command == "build":
        bundle = build_evidence_bundle(root=args.root)
        result = write_outputs(bundle, json_output=args.json_output, markdown_output=args.markdown_output, root=args.root)
        output = {"bundle": bundle, "verification": result}
        print(json.dumps(output, indent=2 if args.pretty else None, sort_keys=True))
    else:
        print(json.dumps(verify_evidence_bundle(load_bundle(args.bundle), root=args.root), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
