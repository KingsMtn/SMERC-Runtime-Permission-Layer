from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, Mapping


GOVERNANCE_BUNDLE_VERSION = "smerc.governance-report-bundle.v1"
GOVERNANCE_REPORT_VERSION = "smerc.governance-report.v1"

BUNDLE_FIELDS = {
    "version",
    "report_id",
    "title",
    "audience",
    "scenario",
    "decision_path",
    "route_report_path",
    "control_mapping_report_path",
    "decision_lifecycle_ledger_path",
    "review_notes",
    "known_limits",
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _strict_object(value: Any, fields: set[str], path: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{path} must be an object")
    missing = sorted(fields - set(value))
    if missing:
        raise ValueError(f"{path} is missing required field(s): {', '.join(missing)}")
    unknown = sorted(set(value) - fields)
    if unknown:
        raise ValueError(f"{path} contains unknown field(s): {', '.join(unknown)}")
    return dict(value)


def _identifier(value: Any, path: str, maximum: int = 128) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,%d}" % (maximum - 1), value):
        raise ValueError(f"{path} must be a safe identifier of 1 to {maximum} characters")
    return value


def _text(value: Any, path: str, maximum: int = 1024) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    value = value.strip()
    if len(value) > maximum:
        raise ValueError(f"{path} must be at most {maximum} characters")
    return value


def _list_of_text(value: Any, path: str, maximum_items: int = 64) -> list[str]:
    if not isinstance(value, list):
        raise TypeError(f"{path} must be a list")
    if len(value) > maximum_items:
        raise ValueError(f"{path} must contain at most {maximum_items} items")
    return [_text(item, f"{path}[]", 256) for item in value]


def _load_json(root: Path, relative_path: str, path_name: str) -> Dict[str, Any]:
    relative_path = _text(relative_path, path_name, 260)
    path = (root / relative_path).resolve()
    root_resolved = root.resolve()
    if root_resolved not in path.parents and path != root_resolved:
        raise ValueError(f"{path_name} must remain inside the repository root")
    with path.open("r", encoding="utf-8-sig") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise TypeError(f"{path_name} must point to a JSON object")
    return payload


def load_bundle(path: str | Path) -> Dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        bundle = _strict_object(json.load(handle), BUNDLE_FIELDS, "governance_bundle")
    if bundle["version"] != GOVERNANCE_BUNDLE_VERSION:
        raise ValueError(f"governance_bundle.version must be {GOVERNANCE_BUNDLE_VERSION}")
    parsed = {
        "version": GOVERNANCE_BUNDLE_VERSION,
        "report_id": _identifier(bundle["report_id"], "governance_bundle.report_id"),
        "title": _text(bundle["title"], "governance_bundle.title", 256),
        "audience": _text(bundle["audience"], "governance_bundle.audience", 256),
        "scenario": _text(bundle["scenario"], "governance_bundle.scenario", 1024),
        "decision_path": _text(bundle["decision_path"], "governance_bundle.decision_path", 260),
        "route_report_path": _text(bundle["route_report_path"], "governance_bundle.route_report_path", 260),
        "control_mapping_report_path": _text(
            bundle["control_mapping_report_path"],
            "governance_bundle.control_mapping_report_path",
            260,
        ),
        "decision_lifecycle_ledger_path": _text(
            bundle["decision_lifecycle_ledger_path"],
            "governance_bundle.decision_lifecycle_ledger_path",
            260,
        ),
        "review_notes": _list_of_text(bundle["review_notes"], "governance_bundle.review_notes"),
        "known_limits": _list_of_text(bundle["known_limits"], "governance_bundle.known_limits"),
    }
    return parsed


def build_report(bundle_path: str | Path, *, repository_root: str | Path = ".") -> Dict[str, Any]:
    root = Path(repository_root)
    bundle = load_bundle(bundle_path)
    decision = _load_json(root, bundle["decision_path"], "decision_path")
    route = _load_json(root, bundle["route_report_path"], "route_report_path")
    control_mapping = _load_json(root, bundle["control_mapping_report_path"], "control_mapping_report_path")
    ledger = _load_json(root, bundle["decision_lifecycle_ledger_path"], "decision_lifecycle_ledger_path")
    checks = _cross_checks(decision, route, control_mapping, ledger)
    artifacts = {
        "decision": _artifact(bundle["decision_path"], decision),
        "route_report": _artifact(bundle["route_report_path"], route),
        "control_mapping_report": _artifact(bundle["control_mapping_report_path"], control_mapping),
        "decision_lifecycle_ledger": _artifact(bundle["decision_lifecycle_ledger_path"], ledger),
    }
    return {
        "version": GOVERNANCE_REPORT_VERSION,
        "report_id": bundle["report_id"],
        "title": bundle["title"],
        "audience": bundle["audience"],
        "scenario": bundle["scenario"],
        "summary": {
            "posture": decision.get("posture"),
            "route_state": route.get("route_state"),
            "route_executable": bool(route.get("executable")),
            "control_mapping_executable": bool(control_mapping.get("executable")),
            "mapped_control_count": len(control_mapping.get("mapped_controls", [])),
            "missing_control_count": len(control_mapping.get("missing_controls", [])),
            "ledger_record_count": ledger.get("record_count"),
            "ledger_valid": bool(ledger.get("verification", {}).get("valid")),
        },
        "cross_checks": checks,
        "artifacts": artifacts,
        "review_notes": bundle["review_notes"],
        "known_limits": bundle["known_limits"],
        "recommended_next_action": _recommended_next_action(checks),
        "plain_english_summary": _summary(decision, route, control_mapping, checks),
    }


def _artifact(path: str, payload: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "path": path,
        "version": payload.get("version", "unversioned"),
        "digest": _sha256(payload),
    }


def _cross_checks(
    decision: Mapping[str, Any],
    route: Mapping[str, Any],
    control_mapping: Mapping[str, Any],
    ledger: Mapping[str, Any],
) -> list[Dict[str, Any]]:
    checks = [
        _check(
            "decision_posture_matches_route_source",
            decision.get("posture") == route.get("source_posture"),
            f"decision posture {decision.get('posture')} vs route source {route.get('source_posture')}",
        ),
        _check(
            "decision_replay_matches_route",
            decision.get("replay_id") == route.get("decision_replay_id"),
            f"decision replay {decision.get('replay_id')} vs route replay {route.get('decision_replay_id')}",
        ),
        _check(
            "route_controls_are_mapped_or_not_required",
            set(route.get("applied_controls", []))
            <= (
                {item.get("control_id") for item in control_mapping.get("mapped_controls", [])}
                | {item.get("control_id") for item in control_mapping.get("not_required_controls", [])}
                | {"checkpoint_before_execution", "record_execution_report"}
            ),
            "route controls should be explainable by the control mapping library or documented as route-level controls",
        ),
        _check(
            "control_mapping_has_no_missing_required_controls",
            control_mapping.get("missing_controls") == [],
            "control mapping should not hide missing native mechanisms",
        ),
        _check(
            "ledger_hash_chain_valid",
            bool(ledger.get("verification", {}).get("valid")),
            "decision lifecycle ledger must verify before being used as evidence",
        ),
    ]
    return checks


def _check(check_id: str, passed: bool, detail: str) -> Dict[str, Any]:
    return {
        "check_id": check_id,
        "passed": bool(passed),
        "detail": detail,
    }


def _recommended_next_action(checks: list[Mapping[str, Any]]) -> str:
    failed = [item["check_id"] for item in checks if not item["passed"]]
    if failed:
        return "Do not use this bundle for pilot approval until failed cross-checks are resolved: " + ", ".join(failed)
    return "Use this bundle as pilot review evidence; validate native enforcement and collect external reviewer feedback before production claims."


def _summary(
    decision: Mapping[str, Any],
    route: Mapping[str, Any],
    control_mapping: Mapping[str, Any],
    checks: list[Mapping[str, Any]],
) -> str:
    failed = sum(1 for item in checks if not item["passed"])
    return (
        f"SMERC returned {decision.get('posture')}; SPARTa routed it to {route.get('route_state')}; "
        f"control mapping executable is {str(bool(control_mapping.get('executable'))).lower()}; "
        f"{failed} cross-check(s) failed."
    )


def render_markdown(report: Mapping[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        f"# {report['title']}",
        "",
        f"Audience: {report['audience']}",
        "",
        "This is a replayable pilot governance report. It assembles existing SMERC artifacts and cross-checks them. It is not production certification, compliance attestation, or proof of live incident reduction.",
        "",
        "## Scenario",
        "",
        report["scenario"],
        "",
        "## Executive Summary",
        "",
        f"- SMERC posture: `{summary['posture']}`",
        f"- SPARTa route state: `{summary['route_state']}`",
        f"- Route executable: `{str(summary['route_executable']).lower()}`",
        f"- Control mapping executable: `{str(summary['control_mapping_executable']).lower()}`",
        f"- Mapped controls: `{summary['mapped_control_count']}`",
        f"- Missing controls: `{summary['missing_control_count']}`",
        f"- DLL records: `{summary['ledger_record_count']}`",
        f"- DLL valid: `{str(summary['ledger_valid']).lower()}`",
        "",
        "## Cross-Checks",
        "",
        "| Check | Result | Detail |",
        "| --- | --- | --- |",
    ]
    for check in report["cross_checks"]:
        result = "pass" if check["passed"] else "fail"
        lines.append(f"| `{check['check_id']}` | `{result}` | {check['detail']} |")
    lines.extend(["", "## Artifacts", "", "| Artifact | Version | Digest |", "| --- | --- | --- |"])
    for name, artifact in report["artifacts"].items():
        lines.append(f"| `{name}`: `{artifact['path']}` | `{artifact['version']}` | `{artifact['digest']}` |")
    lines.extend(["", "## Review Notes", ""])
    lines.extend(f"- {item}" for item in report["review_notes"])
    lines.extend(["", "## Known Limits", ""])
    lines.extend(f"- {item}" for item in report["known_limits"])
    lines.extend(["", "## Recommended Next Action", "", report["recommended_next_action"], "", report["plain_english_summary"], ""])
    return "\n".join(lines)


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a replayable SMERC governance report from existing artifacts.")
    parser.add_argument("bundle", help="Path to a governance report bundle JSON file.")
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--json-output")
    parser.add_argument("--markdown-output")
    args = parser.parse_args()
    report = build_report(args.bundle, repository_root=args.repository_root)
    if args.json_output:
        _write_json(Path(args.json_output), report)
    if args.markdown_output:
        _write_text(Path(args.markdown_output), render_markdown(report))
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
