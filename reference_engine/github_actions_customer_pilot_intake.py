from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping


VERSION = "smerc.github-actions-customer-pilot-intake.v1"
REPORT_VERSION = "smerc.github-actions-customer-pilot-intake-report.v1"

REQUIRED_TOP_LEVEL = {
    "schema",
    "organization",
    "submitted_by_role",
    "intake_date",
    "pilot_goal",
    "workflow",
    "data_boundary",
    "owners",
    "pilot_controls",
    "success_metrics",
    "sample_actions",
}
REQUIRED_WORKFLOW = {
    "repository_scope",
    "workflow_name",
    "workflow_triggers",
    "existing_controls",
    "side_effects",
}
REQUIRED_DATA_BOUNDARY = {
    "metadata_only_confirmed",
    "excluded_data_confirmed",
    "approved_metadata",
    "excluded_data",
    "retention_days",
}
REQUIRED_OWNERS = {
    "security_owner_confirmed",
    "platform_owner_confirmed",
    "reviewer_group_confirmed",
    "business_sponsor_confirmed",
}
REQUIRED_PILOT_CONTROLS = {
    "mode",
    "existing_approvals_remain_authoritative",
    "enforcement_requested",
    "stop_conditions_confirmed",
    "weekly_review_confirmed",
    "day_30_go_no_go_confirmed",
}
REQUIRED_SUCCESS_METRICS = {
    "reviewer_agreement_rate",
    "false_release_candidates",
    "false_constraint_candidates",
    "useful_constraint_rate",
    "override_rate",
    "unavailable_evaluation_count",
    "latency_observations",
}


def load_json(path: str | Path) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return payload


def validate_shape(payload: Mapping[str, Any]) -> Dict[str, Any]:
    _exact_keys(payload, REQUIRED_TOP_LEVEL, "packet")
    if payload["schema"] != VERSION:
        raise ValueError(f"schema must be {VERSION}")
    workflow = _object(payload["workflow"], "workflow")
    data_boundary = _object(payload["data_boundary"], "data_boundary")
    owners = _object(payload["owners"], "owners")
    pilot_controls = _object(payload["pilot_controls"], "pilot_controls")
    success_metrics = _object(payload["success_metrics"], "success_metrics")
    _exact_keys(workflow, REQUIRED_WORKFLOW, "workflow")
    _exact_keys(data_boundary, REQUIRED_DATA_BOUNDARY, "data_boundary")
    _exact_keys(owners, REQUIRED_OWNERS, "owners")
    _exact_keys(pilot_controls, REQUIRED_PILOT_CONTROLS, "pilot_controls")
    _exact_keys(success_metrics, REQUIRED_SUCCESS_METRICS, "success_metrics")
    return {
        "schema": VERSION,
        "organization": _text(payload["organization"], "organization", 160),
        "submitted_by_role": _text(payload["submitted_by_role"], "submitted_by_role", 120),
        "intake_date": _text(payload["intake_date"], "intake_date", 40),
        "pilot_goal": _text(payload["pilot_goal"], "pilot_goal", 500),
        "workflow": {
            "repository_scope": _text(workflow["repository_scope"], "workflow.repository_scope", 240),
            "workflow_name": _text(workflow["workflow_name"], "workflow.workflow_name", 160),
            "workflow_triggers": _string_list(workflow["workflow_triggers"], "workflow.workflow_triggers"),
            "existing_controls": _string_list(workflow["existing_controls"], "workflow.existing_controls"),
            "side_effects": _string_list(workflow["side_effects"], "workflow.side_effects"),
        },
        "data_boundary": {
            "metadata_only_confirmed": _bool(data_boundary["metadata_only_confirmed"], "data_boundary.metadata_only_confirmed"),
            "excluded_data_confirmed": _bool(data_boundary["excluded_data_confirmed"], "data_boundary.excluded_data_confirmed"),
            "approved_metadata": _string_list(data_boundary["approved_metadata"], "data_boundary.approved_metadata"),
            "excluded_data": _string_list(data_boundary["excluded_data"], "data_boundary.excluded_data"),
            "retention_days": _int_range(data_boundary["retention_days"], "data_boundary.retention_days", 1, 90),
        },
        "owners": {key: _bool(owners[key], f"owners.{key}") for key in REQUIRED_OWNERS},
        "pilot_controls": {
            "mode": _text(pilot_controls["mode"], "pilot_controls.mode", 40),
            "existing_approvals_remain_authoritative": _bool(
                pilot_controls["existing_approvals_remain_authoritative"],
                "pilot_controls.existing_approvals_remain_authoritative",
            ),
            "enforcement_requested": _bool(pilot_controls["enforcement_requested"], "pilot_controls.enforcement_requested"),
            "stop_conditions_confirmed": _bool(pilot_controls["stop_conditions_confirmed"], "pilot_controls.stop_conditions_confirmed"),
            "weekly_review_confirmed": _bool(pilot_controls["weekly_review_confirmed"], "pilot_controls.weekly_review_confirmed"),
            "day_30_go_no_go_confirmed": _bool(pilot_controls["day_30_go_no_go_confirmed"], "pilot_controls.day_30_go_no_go_confirmed"),
        },
        "success_metrics": {key: _bool(success_metrics[key], f"success_metrics.{key}") for key in REQUIRED_SUCCESS_METRICS},
        "sample_actions": _string_list(payload["sample_actions"], "sample_actions"),
    }


def assess(payload: Mapping[str, Any]) -> Dict[str, Any]:
    packet = validate_shape(payload)
    blockers: list[str] = []
    warnings: list[str] = []
    if not packet["data_boundary"]["metadata_only_confirmed"]:
        blockers.append("Metadata-only boundary is not confirmed.")
    if not packet["data_boundary"]["excluded_data_confirmed"]:
        blockers.append("Excluded-data boundary is not confirmed.")
    if packet["pilot_controls"]["mode"] != "observe":
        blockers.append("First pilot must start in observe mode.")
    if packet["pilot_controls"]["enforcement_requested"]:
        blockers.append("Enforcement is requested before shadow-mode calibration.")
    if not packet["pilot_controls"]["existing_approvals_remain_authoritative"]:
        blockers.append("Existing approvals must remain authoritative during the first pilot.")
    for key, label in [
        ("security_owner_confirmed", "security owner"),
        ("platform_owner_confirmed", "platform owner"),
        ("reviewer_group_confirmed", "reviewer group"),
    ]:
        if not packet["owners"][key]:
            blockers.append(f"Required {label} is not confirmed.")
    if not packet["pilot_controls"]["stop_conditions_confirmed"]:
        blockers.append("Stop conditions are not confirmed.")
    if not packet["pilot_controls"]["weekly_review_confirmed"]:
        blockers.append("Weekly review is not confirmed.")
    if not packet["pilot_controls"]["day_30_go_no_go_confirmed"]:
        blockers.append("Day-30 go/no-go criteria are not confirmed.")
    if len(packet["sample_actions"]) < 10:
        blockers.append("At least 10 sample action descriptions are required for pilot discussion.")
    if len(packet["sample_actions"]) > 25:
        blockers.append("Use at most 25 sample actions for the first pilot intake.")
    if len(packet["workflow"]["side_effects"]) == 0:
        blockers.append("Workflow side effects are not declared.")
    if not packet["owners"]["business_sponsor_confirmed"]:
        warnings.append("Business sponsor is not confirmed; this can be acceptable for technical review but may block paid pilot approval.")
    if len(packet["workflow"]["existing_controls"]) < 2:
        warnings.append("Few existing controls are listed; reviewers should confirm current approval and rollback mechanisms.")
    missing_metrics = [key for key, value in packet["success_metrics"].items() if not value]
    if missing_metrics:
        blockers.append("Required success metrics are not confirmed: " + ", ".join(sorted(missing_metrics)))

    ready_for_review_call = not blockers
    ready_for_week_zero = ready_for_review_call and not warnings
    return {
        "schema": REPORT_VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "organization": packet["organization"],
        "submitted_by_role": packet["submitted_by_role"],
        "workflow_name": packet["workflow"]["workflow_name"],
        "ready_for_review_call": ready_for_review_call,
        "ready_for_week_zero": ready_for_week_zero,
        "blockers": blockers,
        "warnings": warnings,
        "sample_action_count": len(packet["sample_actions"]),
        "workflow_side_effects": packet["workflow"]["side_effects"],
        "existing_controls": packet["workflow"]["existing_controls"],
        "retention_days": packet["data_boundary"]["retention_days"],
        "recommended_next_action": (
            "Schedule a review call and convert sample actions into smerc.customer-action-intake.v1 metadata."
            if ready_for_review_call
            else "Resolve blockers before asking a customer to start week-zero pilot qualification."
        ),
        "customer_question": (
            "Can SMERC score these actions in observe mode without changing current approvals, "
            "then compare posture output with reviewer judgment for 30 days?"
        ),
        "evidence_boundary": (
            "Customer pilot intake only. It does not prove buyer demand, customer validation, "
            "production safety, incident reduction, compliance, or approval for enforcement."
        ),
    }


def markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# GitHub Actions Customer Pilot Intake Report",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Decision",
        "",
        f"- Organization: `{report['organization']}`",
        f"- Workflow: `{report['workflow_name']}`",
        f"- Ready for review call: `{str(report['ready_for_review_call']).lower()}`",
        f"- Ready for week-zero qualification: `{str(report['ready_for_week_zero']).lower()}`",
        f"- Sample action count: `{report['sample_action_count']}`",
        f"- Retention days: `{report['retention_days']}`",
        "",
        "## Customer Question",
        "",
        str(report["customer_question"]),
        "",
        "## Workflow Side Effects",
        "",
    ]
    lines.extend(f"- {item}" for item in report["workflow_side_effects"])
    lines.extend(["", "## Existing Controls", ""])
    lines.extend(f"- {item}" for item in report["existing_controls"])
    lines.extend(["", "## Blockers", ""])
    if report["blockers"]:
        lines.extend(f"- {item}" for item in report["blockers"])
    else:
        lines.append("- None.")
    lines.extend(["", "## Warnings", ""])
    if report["warnings"]:
        lines.extend(f"- {item}" for item in report["warnings"])
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## Recommended Next Action",
            "",
            str(report["recommended_next_action"]),
            "",
            "## Evidence Boundary",
            "",
            str(report["evidence_boundary"]),
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], json_output: str | Path, markdown_output: str | Path) -> None:
    json_path = Path(json_output)
    markdown_path = Path(markdown_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(markdown(report), encoding="utf-8")


def _exact_keys(payload: Mapping[str, Any], required: set[str], label: str) -> None:
    unknown = sorted(set(payload) - required)
    missing = sorted(required - set(payload))
    if unknown:
        raise ValueError(f"{label} contains unknown field(s): {', '.join(unknown)}")
    if missing:
        raise ValueError(f"{label} is missing field(s): {', '.join(missing)}")


def _object(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{label} must be an object")
    return value


def _text(value: Any, label: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{label} must be a non-empty string")
    text = value.strip()
    if len(text) > maximum:
        raise ValueError(f"{label} must be at most {maximum} characters")
    return text


def _bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{label} must be a boolean")
    return value


def _int_range(value: Any, label: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{label} must be an integer")
    if value < minimum or value > maximum:
        raise ValueError(f"{label} must be between {minimum} and {maximum}")
    return value


def _string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise TypeError(f"{label} must be a non-empty list")
    parsed: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise TypeError(f"{label}[{index}] must be a non-empty string")
        parsed.append(item.strip())
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description="Assess a GitHub Actions customer pilot intake packet.")
    parser.add_argument("path", nargs="?", default="examples/github_actions_customer_pilot_intake_packet.json")
    parser.add_argument("--json-output", default="reports/github_actions_customer_pilot_intake_report.json")
    parser.add_argument("--markdown-output", default="reports/GitHub_Actions_Customer_Pilot_Intake_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = assess(load_json(args.path))
    write_outputs(report, args.json_output, args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
