from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.recoverability_engine import RecoverabilityEngine
from reference_engine.sparta_router import route_decision


VERSION = "smerc.aws-one-action-reviewer-demo.v1"
SAMPLE_VERSION = "smerc.aws-one-action-reviewer-samples.v1"
DEFAULT_INPUT = "examples/aws_one_action_reviewer_samples.json"
DEFAULT_JSON_OUTPUT = "reports/aws_one_action_reviewer_demo/aws_one_action_reviewer_demo.json"
DEFAULT_MARKDOWN_OUTPUT = "reports/aws_one_action_reviewer_demo/AWS_One_Action_Reviewer_Demo.md"

RECOVERABILITY_FIELDS = {
    "action_id",
    "description",
    "actor",
    "tool",
    "action_type",
    "base_action_risk",
    "reversibility",
    "containment_strength",
    "rollback_latency",
    "evidence_validity",
    "anomaly_pressure",
    "impact_scope",
    "cancel_reliability",
    "authorization_confidence",
    "external_side_effect",
    "sensitive_data",
    "context",
}


def load_payload(path: str | Path = DEFAULT_INPUT) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("AWS one-action reviewer payload must be a JSON object")
    if payload.get("version") != SAMPLE_VERSION:
        raise ValueError(f"version must be {SAMPLE_VERSION}")
    actions = payload.get("actions")
    if not isinstance(actions, list) or not actions:
        raise ValueError("actions must be a non-empty list")
    if len(actions) > 10:
        raise ValueError("AWS one-action reviewer samples should stay small: at most 10 actions")
    return payload


def build_report(payload: Mapping[str, Any], action_id: str | None = None) -> Dict[str, Any]:
    actions = _select_actions(payload, action_id)
    records = [_evaluate_action(action) for action in actions]
    posture_counts = Counter(record["posture"] for record in records)
    route_counts = Counter(record["route_state"] for record in records)
    surface_counts = Counter(record["aws_surface"] for record in records)
    return {
        "version": VERSION,
        "generated_at": _now(),
        "source_version": payload["version"],
        "selected_action_id": action_id or "all",
        "sample_count": len(records),
        "data_boundary": payload["data_boundary"],
        "evidence_boundary": (
            "This is a metadata-only AWS-style one-action reviewer demo. It does not connect to AWS, inspect "
            "CloudTrail, invoke Lambda, modify IAM, change S3, execute CloudFormation, scale compute, delete "
            "databases, rotate secrets, spend money, read customer systems, or prove production safety."
        ),
        "summary": {
            "posture_counts": dict(sorted(posture_counts.items())),
            "route_state_counts": dict(sorted(route_counts.items())),
            "aws_surface_counts": dict(sorted(surface_counts.items())),
            "non_executable_routes": sum(1 for record in records if not record["executable"]),
            "highest_exposure_action": max(
                records,
                key=lambda record: record["scores"]["irreversible_exposure_score"],
            )["action_id"],
        },
        "records": records,
        "recommended_reviewer_ask": (
            "Pick the closest sample, replace only safe metadata with one real action from your workflow, and tell "
            "us whether the posture and route match how your team would handle the action."
        ),
    }


def _select_actions(payload: Mapping[str, Any], action_id: str | None) -> list[Mapping[str, Any]]:
    actions = payload["actions"]
    if not action_id:
        return list(actions)
    selected = [action for action in actions if action.get("action_id") == action_id]
    if not selected:
        available = ", ".join(sorted(str(action.get("action_id")) for action in actions))
        raise ValueError(f"Unknown action_id {action_id}. Available action IDs: {available}")
    return selected


def _evaluate_action(action: Mapping[str, Any]) -> Dict[str, Any]:
    _validate_action(action)
    decision = RecoverabilityEngine().evaluate(_recoverability_payload(action))
    route = route_decision(decision, action["tool_plan"])
    metadata = action["tool_plan"]["metadata"]
    scores = decision["scores"]
    return {
        "action_id": action["action_id"],
        "description": action["description"],
        "aws_surface": metadata.get("aws_surface", action["context"].get("aws_surface", "aws")),
        "change_family": metadata.get("change_family", action["context"].get("change_family", "unknown")),
        "posture": decision["posture"],
        "route_state": route["route_state"],
        "executable": route["executable"],
        "effective_scope_units": route["effective_scope_units"],
        "scores": scores,
        "reason_codes": decision["reason_codes"],
        "controls": decision["controls"],
        "applied_route_controls": route["applied_controls"],
        "transition_guidance": decision["transition_guidance"],
        "plain_english_summary": decision["plain_english_summary"],
        "why": _why(action, decision, route),
    }


def _validate_action(action: Mapping[str, Any]) -> None:
    missing = sorted((RECOVERABILITY_FIELDS | {"tool_plan"}) - set(action))
    if missing:
        raise ValueError(f"action is missing required field(s): {', '.join(missing)}")
    unknown = sorted(set(action) - RECOVERABILITY_FIELDS - {"tool_plan"})
    if unknown:
        raise ValueError(f"action contains unknown field(s): {', '.join(unknown)}")
    if not isinstance(action["tool_plan"], dict):
        raise TypeError("action.tool_plan must be an object")


def _recoverability_payload(action: Mapping[str, Any]) -> Dict[str, Any]:
    return {key: action[key] for key in RECOVERABILITY_FIELDS}


def _why(action: Mapping[str, Any], decision: Mapping[str, Any], route: Mapping[str, Any]) -> Dict[str, str]:
    scores = decision["scores"]
    posture = decision["posture"]
    if posture == "ALLOW":
        result = "SMERC found enough recovery capacity, confidence, and containment to allow execution with replay evidence."
    elif posture == "THROTTLE":
        result = "SMERC found the action potentially useful, but only safe through reduced scope, preview, checkpointing, or rollback controls."
    elif posture == "FREEZE":
        result = "SMERC found the action too uncertain to run now, so execution pauses while evidence, rollback, or containment is repaired."
    elif posture == "DENY":
        result = "SMERC found the action structurally unsafe in this form, so execution is blocked until a materially safer request is submitted."
    else:
        result = "SMERC found that accountable review is needed before execution can be considered."

    return {
        "work": f"Evaluate AWS-style `{action['tool']}` action `{action['action_id']}` before execution.",
        "result": (
            f"Returned `{posture}`, routed `{route['route_state']}`, exposure "
            f"`{scores['irreversible_exposure_score']}`, recovery capacity "
            f"`{scores['reversible_capacity_score']}`, confidence `{scores['confidence_score']}`."
        ),
        "impact": result,
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# AWS One-Action Reviewer Demo",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Version: `{report['version']}`",
        "",
        "## Purpose",
        "",
        "This is the quickest AWS-style review path for SMERC: choose one safe metadata-only action, run it locally, and inspect posture, route, reason codes, scores, and transition guidance.",
        "",
        "## Evidence Boundary",
        "",
        str(report["evidence_boundary"]),
        "",
        "## Summary",
        "",
        f"- Actions evaluated: `{report['sample_count']}`",
        f"- Posture counts: `{report['summary']['posture_counts']}`",
        f"- Route state counts: `{report['summary']['route_state_counts']}`",
        f"- AWS surface counts: `{report['summary']['aws_surface_counts']}`",
        f"- Non-executable routes: `{report['summary']['non_executable_routes']}`",
        f"- Highest exposure action: `{report['summary']['highest_exposure_action']}`",
        "",
        "## Results",
        "",
        "| Action | Surface | Posture | Route | Executable | Exposure | Recovery | Reason codes |",
        "| --- | --- | --- | --- | --- | ---: | ---: | --- |",
    ]
    for record in report["records"]:
        codes = ", ".join(f"`{code}`" for code in record["reason_codes"][:5])
        lines.append(
            f"| `{record['action_id']}` | `{record['aws_surface']}` | `{record['posture']}` | "
            f"`{record['route_state']}` | `{record['executable']}` | "
            f"{record['scores']['irreversible_exposure_score']} | "
            f"{record['scores']['reversible_capacity_score']} | {codes} |"
        )
    lines.extend(["", "## Why It Judged That Way", ""])
    for record in report["records"]:
        lines.extend(
            [
                f"### {record['action_id']}",
                "",
                f"- Work: {record['why']['work']}",
                f"- Result: {record['why']['result']}",
                f"- Impact: {record['why']['impact']}",
                f"- Controls: `{record['controls']}`",
                f"- Route controls: `{record['applied_route_controls']}`",
                f"- Transition guidance: `{record['transition_guidance']}`",
                "",
            ]
        )
    lines.extend(["## Recommended Reviewer Ask", "", str(report["recommended_reviewer_ask"]), ""])
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], json_output: str | Path, markdown_output: str | Path) -> None:
    json_path = Path(json_output)
    markdown_path = Path(markdown_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the AWS-style SMERC one-action reviewer demo.")
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--action-id", help="Evaluate one named sample instead of the full small set.")
    parser.add_argument("--json-output", default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--markdown-output", default=DEFAULT_MARKDOWN_OUTPUT)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_report(load_payload(args.input), action_id=args.action_id)
    write_outputs(report, args.json_output, args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
