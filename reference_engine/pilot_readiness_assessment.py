from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping


READINESS_VERSION = "smerc.pilot-readiness.v1"
VALID_STATUSES = {"met", "partial", "not_met"}


def _require_text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    return value.strip()


def _require_bool(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{path} must be a boolean")
    return value


def _require_paths(value: Any, path: str) -> list[str]:
    if not isinstance(value, list):
        raise TypeError(f"{path} must be a list")
    paths = []
    for index, item in enumerate(value):
        item = _require_text(item, f"{path}[{index}]")
        if item.startswith("/") or ":" in item or "\\" in item:
            raise ValueError(f"{path}[{index}] must be a repository-relative POSIX path")
        if ".." in Path(item).parts:
            raise ValueError(f"{path}[{index}] must not traverse parent directories")
        paths.append(item)
    return paths


def validate_payload(payload: Mapping[str, Any]) -> Dict[str, Any]:
    required = {"version", "project", "target_level", "assessment_date", "summary", "gates"}
    unknown = sorted(set(payload) - required)
    missing = sorted(required - set(payload))
    if unknown:
        raise ValueError(f"readiness payload contains unknown field(s): {', '.join(unknown)}")
    if missing:
        raise ValueError(f"readiness payload is missing field(s): {', '.join(missing)}")
    if payload["version"] != READINESS_VERSION:
        raise ValueError(f"version must be {READINESS_VERSION}")
    gates = payload["gates"]
    if not isinstance(gates, list) or not gates:
        raise TypeError("gates must be a non-empty list")
    parsed_gates = []
    seen = set()
    for index, gate in enumerate(gates):
        if not isinstance(gate, dict):
            raise TypeError(f"gates[{index}] must be an object")
        gate_required = {"id", "label", "status", "required", "evidence_paths", "notes"}
        gate_unknown = sorted(set(gate) - gate_required)
        gate_missing = sorted(gate_required - set(gate))
        if gate_unknown:
            raise ValueError(f"gates[{index}] contains unknown field(s): {', '.join(gate_unknown)}")
        if gate_missing:
            raise ValueError(f"gates[{index}] is missing field(s): {', '.join(gate_missing)}")
        gate_id = _require_text(gate["id"], f"gates[{index}].id")
        if gate_id in seen:
            raise ValueError(f"duplicate gate id: {gate_id}")
        seen.add(gate_id)
        status = _require_text(gate["status"], f"gates[{index}].status")
        if status not in VALID_STATUSES:
            raise ValueError(f"gates[{index}].status must be one of {', '.join(sorted(VALID_STATUSES))}")
        parsed_gates.append(
            {
                "id": gate_id,
                "label": _require_text(gate["label"], f"gates[{index}].label"),
                "status": status,
                "required": _require_bool(gate["required"], f"gates[{index}].required"),
                "evidence_paths": _require_paths(gate["evidence_paths"], f"gates[{index}].evidence_paths"),
                "notes": _require_text(gate["notes"], f"gates[{index}].notes"),
            }
        )
    return {
        "version": READINESS_VERSION,
        "project": _require_text(payload["project"], "project"),
        "target_level": _require_text(payload["target_level"], "target_level"),
        "assessment_date": _require_text(payload["assessment_date"], "assessment_date"),
        "summary": _require_text(payload["summary"], "summary"),
        "gates": parsed_gates,
    }


def assess(payload: Mapping[str, Any], *, repo_root: Path) -> Dict[str, Any]:
    readiness = validate_payload(payload)
    gate_results = []
    required_failures = []
    missing_evidence = []
    for gate in readiness["gates"]:
        missing_paths = [
            path for path in gate["evidence_paths"]
            if not (repo_root / path).exists()
        ]
        gate_result = dict(gate)
        gate_result["missing_evidence_paths"] = missing_paths
        gate_result["evidence_path_count"] = len(gate["evidence_paths"])
        gate_result["evidence_present"] = not missing_paths
        gate_results.append(gate_result)
        if missing_paths:
            missing_evidence.append(gate["id"])
        if gate["required"] and gate["status"] != "met":
            required_failures.append(gate["id"])
        if gate["required"] and missing_paths:
            required_failures.append(f"{gate['id']}:missing_evidence")

    required_gates = [gate for gate in gate_results if gate["required"]]
    optional_gates = [gate for gate in gate_results if not gate["required"]]
    level5_ready = not required_failures
    return {
        "version": readiness["version"],
        "project": readiness["project"],
        "target_level": readiness["target_level"],
        "assessment_date": readiness["assessment_date"],
        "summary": readiness["summary"],
        "level5_shadow_mode_ready": level5_ready,
        "required_gate_count": len(required_gates),
        "required_met_count": sum(1 for gate in required_gates if gate["status"] == "met" and gate["evidence_present"]),
        "optional_gate_count": len(optional_gates),
        "optional_met_count": sum(1 for gate in optional_gates if gate["status"] == "met" and gate["evidence_present"]),
        "required_failures": required_failures,
        "gates_missing_evidence": missing_evidence,
        "gates": gate_results,
    }


def load_readiness(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise TypeError("readiness file must contain a JSON object")
    return payload


def write_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        f"# {report['project']} Pilot Readiness Assessment",
        "",
        f"Target: {report['target_level']}",
        f"Assessment date: {report['assessment_date']}",
        "",
        report["summary"],
        "",
        "## Result",
        "",
        f"Level 5 shadow-mode ready: {'yes' if report['level5_shadow_mode_ready'] else 'no'}",
        f"Required gates met: {report['required_met_count']} of {report['required_gate_count']}",
        f"Optional gates met: {report['optional_met_count']} of {report['optional_gate_count']}",
        "",
        "## Required Failures",
        "",
    ]
    if report["required_failures"]:
        lines.extend(f"- {item}" for item in report["required_failures"])
    else:
        lines.append("- None.")
    lines.extend(["", "## Gate Results", ""])
    for gate in report["gates"]:
        lines.extend(
            [
                f"### {gate['label']}",
                "",
                f"- Gate ID: `{gate['id']}`",
                f"- Required: {'yes' if gate['required'] else 'no'}",
                f"- Status: `{gate['status']}`",
                f"- Evidence paths present: {'yes' if gate['evidence_present'] else 'no'}",
                f"- Notes: {gate['notes']}",
            ]
        )
        if gate["evidence_paths"]:
            lines.append("- Evidence:")
            lines.extend(f"  - `{path}`" for path in gate["evidence_paths"])
        if gate["missing_evidence_paths"]:
            lines.append("- Missing evidence:")
            lines.extend(f"  - `{path}`" for path in gate["missing_evidence_paths"])
        lines.append("")
    lines.extend(
        [
            "## Interpretation",
            "",
            "This assessment supports a shadow-mode pilot discussion only. It does not assert production readiness, customer validation, compliance certification, or incident-reduction proof.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Assess SMERC Level 5 pilot readiness evidence.")
    parser.add_argument("readiness_file", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = assess(load_readiness(args.readiness_file), repo_root=args.repo_root)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
