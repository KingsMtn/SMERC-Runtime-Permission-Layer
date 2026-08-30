from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping


VERSION = "smerc.external-reviewer-metadata-response-assessment.v1"
INPUT_VERSION = "smerc.external-reviewer-metadata-response.v1"
WORKFLOW_FAMILIES = {"general", "cloud", "financial"}


def load_payload(path: str | Path) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("external reviewer metadata response must be a JSON object")
    return payload


def assess_response(payload: Mapping[str, Any]) -> Dict[str, Any]:
    parsed = _validate_payload(payload)
    blockers: list[str] = []
    warnings: list[str] = []

    if parsed["sensitive_data_included"]:
        blockers.append("Reviewer response includes sensitive data; stop and request metadata-only replacement.")
    if parsed["live_access_requested"]:
        blockers.append("Reviewer response asks for live access; keep the first review offline and metadata-only.")
    if not parsed["metadata_only_confirmed"]:
        blockers.append("Metadata-only boundary is not confirmed.")
    if parsed["provided_action_count"] < 5:
        blockers.append("At least 5 metadata-only actions are needed for a first reviewer-owned evaluation.")
    if parsed["provided_action_count"] > 25:
        blockers.append("Use at most 25 actions for the first reviewer-owned evaluation.")
    if not parsed["current_control_outcomes_included"]:
        warnings.append("Current control outcomes are missing; SMERC can score actions, but comparison value is weaker.")
    if not parsed["reviewer_labels_available"]:
        warnings.append("Reviewer labels are not available; shadow-mode pilot evidence will be weak.")
    if not parsed["postcondition_observation_possible"]:
        warnings.append("Postcondition observation is not available; SMERC can recommend controls but cannot yet verify that controls happened.")
    if parsed["performance_threshold_p95_ms"] <= 0:
        warnings.append("No p95 threshold supplied; use local performance evidence only as a baseline.")

    ready = not blockers
    if ready and parsed["current_control_outcomes_included"] and parsed["reviewer_labels_available"]:
        disposition = "ready_for_customer_metadata_evaluation"
    elif ready:
        disposition = "ready_with_review_limits"
    else:
        disposition = "not_ready"

    return {
        "version": VERSION,
        "generated_at": _now(),
        "organization_alias": parsed["organization_alias"],
        "reviewer_role": parsed["reviewer_role"],
        "workflow_family": parsed["workflow_family"],
        "provided_action_count": parsed["provided_action_count"],
        "disposition": disposition,
        "ready_for_customer_metadata_evaluation": ready,
        "blockers": blockers,
        "warnings": warnings,
        "recommended_next_action": _recommend(disposition),
        "work_result_impact": {
            "work": "Assess whether an external reviewer response is safe and useful enough to replace public examples.",
            "result": f"Response disposition is {disposition} for {parsed['provided_action_count']} metadata action(s).",
            "impact": (
                "SMERC can move from public synthetic proof to reviewer-owned metadata only when the data boundary, "
                "comparison labels, postcondition observation, and performance expectations are explicit."
            ),
        },
        "evidence_boundary": (
            "This assessment screens reviewer-supplied metadata readiness. It does not prove customer demand, "
            "production safety, incident reduction, compliance, or approval for enforcement."
        ),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# External Reviewer Metadata Response Assessment",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Version: `{report['version']}`",
        f"Organization alias: `{report['organization_alias']}`",
        f"Reviewer role: `{report['reviewer_role']}`",
        f"Workflow family: `{report['workflow_family']}`",
        f"Provided actions: `{report['provided_action_count']}`",
        f"Disposition: `{report['disposition']}`",
        "",
        "## Work / Result / Impact",
        "",
        f"- Work: {report['work_result_impact']['work']}",
        f"- Result: {report['work_result_impact']['result']}",
        f"- Impact: {report['work_result_impact']['impact']}",
        "",
        "## Blockers",
        "",
    ]
    lines.extend(f"- {item}" for item in report["blockers"] or ["None."])
    lines.extend(["", "## Warnings", ""])
    lines.extend(f"- {item}" for item in report["warnings"] or ["None."])
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


def write_outputs(report: Mapping[str, Any], *, json_path: str | Path, markdown_path: str | Path) -> None:
    json_output = Path(json_path)
    markdown_output = Path(markdown_path)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_output.write_text(render_markdown(report), encoding="utf-8")


def _validate_payload(payload: Mapping[str, Any]) -> Dict[str, Any]:
    required = {
        "schema",
        "organization_alias",
        "reviewer_role",
        "workflow_family",
        "provided_action_count",
        "metadata_only_confirmed",
        "sensitive_data_included",
        "live_access_requested",
        "current_control_outcomes_included",
        "reviewer_labels_available",
        "performance_threshold_p95_ms",
        "postcondition_observation_possible",
        "notes",
    }
    unknown = sorted(set(payload) - required)
    missing = sorted(required - set(payload))
    if unknown:
        raise ValueError(f"external reviewer response contains unknown field(s): {', '.join(unknown)}")
    if missing:
        raise ValueError(f"external reviewer response is missing field(s): {', '.join(missing)}")
    if payload["schema"] != INPUT_VERSION:
        raise ValueError(f"schema must be {INPUT_VERSION}")
    workflow_family = _text(payload["workflow_family"], "workflow_family", 40)
    if workflow_family not in WORKFLOW_FAMILIES:
        raise ValueError(f"workflow_family must be one of: {', '.join(sorted(WORKFLOW_FAMILIES))}")
    return {
        "organization_alias": _text(payload["organization_alias"], "organization_alias", 160),
        "reviewer_role": _text(payload["reviewer_role"], "reviewer_role", 120),
        "workflow_family": workflow_family,
        "provided_action_count": _integer(payload["provided_action_count"], "provided_action_count"),
        "metadata_only_confirmed": _boolean(payload["metadata_only_confirmed"], "metadata_only_confirmed"),
        "sensitive_data_included": _boolean(payload["sensitive_data_included"], "sensitive_data_included"),
        "live_access_requested": _boolean(payload["live_access_requested"], "live_access_requested"),
        "current_control_outcomes_included": _boolean(
            payload["current_control_outcomes_included"], "current_control_outcomes_included"
        ),
        "reviewer_labels_available": _boolean(payload["reviewer_labels_available"], "reviewer_labels_available"),
        "performance_threshold_p95_ms": _integer(payload["performance_threshold_p95_ms"], "performance_threshold_p95_ms"),
        "postcondition_observation_possible": _boolean(
            payload["postcondition_observation_possible"], "postcondition_observation_possible"
        ),
        "notes": _text(payload["notes"], "notes", 1000),
    }


def _recommend(disposition: str) -> str:
    if disposition == "ready_for_customer_metadata_evaluation":
        return "Run the customer-owned metadata evaluation, postcondition evidence path, and serious report performance harness."
    if disposition == "ready_with_review_limits":
        return "Run metadata evaluation only as a limited review and ask for missing labels, postcondition observations, or p95 thresholds."
    return "Do not run a customer-specific package yet; remove blockers and re-confirm the metadata-only boundary."


def _text(value: Any, field: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{field} must be a non-empty string")
    result = value.strip()
    if len(result) > maximum:
        raise ValueError(f"{field} must be at most {maximum} characters")
    return result


def _boolean(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{field} must be boolean")
    return value


def _integer(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{field} must be an integer")
    return value


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Assess an external reviewer metadata response for SMERC.")
    parser.add_argument("path", nargs="?", default="examples/external_reviewer_metadata_response_example.json")
    parser.add_argument("--json-output", default="reports/external_reviewer_metadata_response_assessment.json")
    parser.add_argument("--markdown-output", default="reports/External_Reviewer_Metadata_Response_Assessment.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = assess_response(load_payload(args.path))
    write_outputs(report, json_path=args.json_output, markdown_path=args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
