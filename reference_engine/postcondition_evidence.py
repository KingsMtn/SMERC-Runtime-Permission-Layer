from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping


VERSION = "smerc.postcondition-evidence.v1"
OBSERVATION_STATUSES = {"succeeded", "failed", "not_executed", "held_for_review", "rolled_back"}
CONTROL_OUTCOMES = {"applied", "failed", "missing", "not_applicable"}


def load_json_object(path: str | Path) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return payload


def load_observations(path: str | Path) -> list[Dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError("postcondition observations must be a non-empty JSON array")
    rows: list[Dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise TypeError(f"observations[{index}] must be an object")
        action_id = _text(item.get("action_id"), f"observations[{index}].action_id")
        if action_id in seen:
            raise ValueError(f"duplicate observation action_id: {action_id}")
        seen.add(action_id)
        rows.append(_normalize_observation(item, index))
    return rows


def build_postcondition_report(evaluation: Mapping[str, Any], observations: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    records = evaluation.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("evaluation must include non-empty records")
    observation_by_action = {str(item["action_id"]): dict(item) for item in observations}

    assessed = []
    status_counts: Counter[str] = Counter()
    coverage_counts: Counter[str] = Counter()
    for record in records:
        action_id = _text(record.get("action_id"), "record.action_id")
        route = record.get("sparta_route")
        if not isinstance(route, dict):
            raise ValueError(f"{action_id} is missing sparta_route")
        observation = observation_by_action.get(action_id)
        item = _assess_record(action_id, record, route, observation)
        assessed.append(item)
        status_counts[item["postcondition_status"]] += 1
        coverage_counts[item["coverage"]] += 1

    return {
        "version": VERSION,
        "generated_at": _now(),
        "source_evaluation_version": str(evaluation.get("version", "unknown")),
        "source_organization": str(evaluation.get("organization", "unknown")),
        "evaluated_actions": len(assessed),
        "observed_actions": sum(1 for item in assessed if item["coverage"] == "observed"),
        "coverage_counts": dict(sorted(coverage_counts.items())),
        "postcondition_status_counts": dict(sorted(status_counts.items())),
        "records": assessed,
        "evidence_boundary": (
            "This report compares declared SMERC/SPARTa route controls with supplied observation metadata. "
            "It proves postcondition accounting mechanics, not live cloud, GitHub, MCP, financial, or production enforcement. "
            "Customer pilots must bind observations to native platform records or signed adapter evidence."
        ),
        "work_result_impact": {
            "work": "Compare required SPARTa controls against observed post-action or held-action evidence.",
            "result": (
                f"Assessed {len(assessed)} routed actions, found "
                f"{status_counts.get('pass', 0)} pass, {status_counts.get('gap', 0)} gap, "
                f"{status_counts.get('violation', 0)} violation, and {status_counts.get('unobserved', 0)} unobserved statuses."
            ),
            "impact": (
                "SMERC can now show whether controls were actually observed after a route, not only whether it recommended them."
            ),
        },
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC Postcondition Evidence Report",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Version: `{report['version']}`",
        f"Source evaluation: `{report['source_evaluation_version']}`",
        "",
        "## Purpose",
        "",
        "This report checks whether the controls required by SMERC and SPARTa were actually observed after the route decision.",
        "",
        "## Work / Result / Impact",
        "",
        f"- Work: {report['work_result_impact']['work']}",
        f"- Result: {report['work_result_impact']['result']}",
        f"- Impact: {report['work_result_impact']['impact']}",
        "",
        "## Evidence Boundary",
        "",
        str(report["evidence_boundary"]),
        "",
        "## Summary",
        "",
        f"- Evaluated actions: `{report['evaluated_actions']}`",
        f"- Observed actions: `{report['observed_actions']}`",
        f"- Coverage counts: `{report['coverage_counts']}`",
        f"- Postcondition status counts: `{report['postcondition_status_counts']}`",
        "",
        "## Action Checks",
        "",
        "| Action | Route | Executable | Execution | Missing controls | Failed controls | Status |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in report["records"]:
        lines.append(
            f"| `{item['action_id']}` | `{item['route_state']}` | `{item['route_executable']}` | "
            f"`{item['execution_status']}` | `{item['missing_controls']}` | `{item['failed_controls']}` | "
            f"`{item['postcondition_status']}` |"
        )
    lines.extend(
        [
            "",
            "## Reviewer Question",
            "",
            "Can a real adapter produce signed or platform-native evidence for each required control before an executable route is allowed to complete?",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], *, json_path: str | Path, markdown_path: str | Path) -> None:
    json_output = Path(json_path)
    markdown_output = Path(markdown_path)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_output.write_text(render_markdown(report), encoding="utf-8")


def _assess_record(
    action_id: str,
    record: Mapping[str, Any],
    route: Mapping[str, Any],
    observation: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    required = sorted(set(_controls(route.get("applied_controls"), f"{action_id}.sparta_route.applied_controls")))
    if observation is None:
        return {
            "action_id": action_id,
            "route_state": str(route.get("route_state")),
            "route_executable": bool(route.get("executable")),
            "source_posture": str(record.get("decision", {}).get("posture", "unknown")),
            "coverage": "unobserved",
            "required_controls": required,
            "observed_controls": [],
            "missing_controls": required,
            "failed_controls": [],
            "unexpected_controls": [],
            "execution_attempted": None,
            "execution_status": "unobserved",
            "postcondition_status": "unobserved",
            "findings": ["No postcondition observation was supplied for this routed action."],
        }

    observed_results = list(observation["observed_controls"])
    applied = sorted(item["control_id"] for item in observed_results if item["outcome"] == "applied")
    failed = sorted(item["control_id"] for item in observed_results if item["outcome"] == "failed")
    observed_ids = sorted(set(item["control_id"] for item in observed_results))
    missing = sorted(set(required) - set(applied))
    unexpected = sorted(set(observed_ids) - set(required))
    execution = observation["execution"]
    attempted = bool(execution["attempted"])
    execution_status = str(execution["status"])
    executable = bool(route.get("executable"))
    findings = []

    if missing:
        findings.append(f"Missing required control evidence: {', '.join(missing)}.")
    if failed:
        findings.append(f"Failed control evidence: {', '.join(failed)}.")
    if not executable and attempted:
        findings.append("Execution was attempted even though the SPARTa route was not executable.")
    if executable and not attempted:
        findings.append("Executable route did not include an execution attempt.")
    if execution_status == "failed" and not execution.get("rollback_performed"):
        findings.append("Execution failed without recorded rollback.")

    if not executable and attempted:
        status = "violation"
    elif missing or failed or (executable and not attempted) or (execution_status == "failed" and not execution.get("rollback_performed")):
        status = "gap"
    else:
        status = "pass"
    if not findings:
        findings.append("Observed evidence satisfies required route controls for this metadata-only proof.")

    return {
        "action_id": action_id,
        "route_state": str(route.get("route_state")),
        "route_executable": executable,
        "source_posture": str(record.get("decision", {}).get("posture", "unknown")),
        "coverage": "observed",
        "required_controls": required,
        "observed_controls": observed_ids,
        "missing_controls": missing,
        "failed_controls": failed,
        "unexpected_controls": unexpected,
        "execution_attempted": attempted,
        "execution_status": execution_status,
        "postcondition_status": status,
        "findings": findings,
    }


def _normalize_observation(item: Mapping[str, Any], index: int) -> Dict[str, Any]:
    controls = item.get("observed_controls")
    if not isinstance(controls, list):
        raise TypeError(f"observations[{index}].observed_controls must be a list")
    normalized_controls = []
    seen = set()
    for control_index, control in enumerate(controls):
        if not isinstance(control, dict):
            raise TypeError(f"observations[{index}].observed_controls[{control_index}] must be an object")
        control_id = _text(control.get("control_id"), f"observations[{index}].observed_controls[{control_index}].control_id")
        if control_id in seen:
            raise ValueError(f"duplicate observed control {control_id} for action {item['action_id']}")
        seen.add(control_id)
        outcome = _text(control.get("outcome"), f"{control_id}.outcome")
        if outcome not in CONTROL_OUTCOMES:
            raise ValueError(f"{control_id}.outcome must be one of {', '.join(sorted(CONTROL_OUTCOMES))}")
        normalized_controls.append(
            {
                "control_id": control_id,
                "outcome": outcome,
                "mechanism": _text(control.get("mechanism"), f"{control_id}.mechanism", 160),
                "evidence_ref": _text(control.get("evidence_ref"), f"{control_id}.evidence_ref", 256),
                "observed_at": _text(control.get("observed_at"), f"{control_id}.observed_at", 64),
            }
        )
    execution = item.get("execution")
    if not isinstance(execution, dict):
        raise TypeError(f"observations[{index}].execution must be an object")
    status = _text(execution.get("status"), f"observations[{index}].execution.status")
    if status not in OBSERVATION_STATUSES:
        raise ValueError(f"execution.status must be one of {', '.join(sorted(OBSERVATION_STATUSES))}")
    rollback_success = execution.get("rollback_success")
    if rollback_success is not None and not isinstance(rollback_success, bool):
        raise TypeError("execution.rollback_success must be boolean or null")
    return {
        "action_id": _text(item.get("action_id"), f"observations[{index}].action_id"),
        "observed_controls": sorted(normalized_controls, key=lambda value: value["control_id"]),
        "execution": {
            "attempted": _boolean(execution.get("attempted"), "execution.attempted"),
            "status": status,
            "rollback_performed": _boolean(execution.get("rollback_performed"), "execution.rollback_performed"),
            "rollback_success": rollback_success,
            "notes": _text(execution.get("notes"), "execution.notes", 320),
        },
    }


def _controls(values: Any, path: str) -> list[str]:
    if not isinstance(values, list) or any(not isinstance(item, str) or not item.strip() for item in values):
        raise TypeError(f"{path} must be a list of non-empty strings")
    return [item.strip() for item in values]


def _text(value: Any, path: str, maximum: int = 128) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    clean = value.strip()
    if len(clean) > maximum:
        raise ValueError(f"{path} must be at most {maximum} characters")
    return clean


def _boolean(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{path} must be a boolean")
    return value


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare SMERC/SPARTa route controls with observed postcondition evidence.")
    parser.add_argument("--evaluation", required=True, type=Path, help="Path to a SMERC customer-evaluation JSON report.")
    parser.add_argument("--observations", required=True, type=Path, help="Path to postcondition observation JSON.")
    parser.add_argument("--json-output", default="reports/postcondition_evidence_report.json")
    parser.add_argument("--markdown-output", default="reports/Postcondition_Evidence_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_postcondition_report(load_json_object(args.evaluation), load_observations(args.observations))
    write_outputs(report, json_path=args.json_output, markdown_path=args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
