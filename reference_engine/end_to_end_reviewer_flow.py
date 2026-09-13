from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine import dynamic_schema_gate, local_shadow_intake
from reference_engine.spl import compile_spl_file


VERSION = "smerc.end-to-end-reviewer-flow.v1"
SOURCE_NAME = "SMERC End-to-End Reviewer Flow"

POSTURE_TO_ROUTE = {
    "ALLOW": "EXECUTE",
    "THROTTLE": "CONSTRAINED_EXECUTE",
    "FREEZE": "PAUSE",
    "DENY": "BLOCK",
    "ESCALATE": "REVIEW_REQUIRED",
}


def build_flow_report(
    *,
    intake_path: str | Path = "examples/local_shadow_intake_examples.json",
    schema_gate_path: str | Path = "examples/dynamic_schema_gate_examples.json",
    policy_path: str | Path = "examples/policies/github_actions_shadow_spl.json",
) -> Dict[str, Any]:
    intake_report = local_shadow_intake.build_intake_report(local_shadow_intake.load_payload(intake_path))
    schema_report = dynamic_schema_gate.build_report(dynamic_schema_gate.load_payload(schema_gate_path))
    policy = compile_spl_file(policy_path)
    accepted_actions = intake_report["sanitized_metadata_draft"]["actions"]
    posture_counts = Counter(action["intake_posture_hint"] for action in accepted_actions)
    route_counts = Counter(POSTURE_TO_ROUTE[action["intake_posture_hint"]] for action in accepted_actions)
    posture_rows = [_posture_row(action, policy.decision_metadata()) for action in accepted_actions]
    stage_results = [
        _stage(
            "metadata_intake",
            "PASS" if intake_report["accepted_action_count"] >= 5 else "NEEDS_MORE_DATA",
            (
                f"Accepted {intake_report['accepted_action_count']} of {intake_report['input_action_count']} "
                "metadata-only action summaries."
            ),
        ),
        _stage(
            "schema_validation",
            "PASS" if schema_report["tool_call_count"] > 0 else "NEEDS_MORE_DATA",
            (
                f"Evaluated {schema_report['tool_call_count']} dynamic tool calls against "
                f"{schema_report['registry_count']} pinned schema entries."
            ),
        ),
        _stage(
            "policy_evaluation",
            "PASS",
            (
                f"Compiled SPL policy {policy.policy_id}@{policy.policy_revision} in {policy.mode} mode "
                f"with evidence ceiling {policy.evidence_ceiling}."
            ),
        ),
        _stage(
            "posture_output",
            "PASS" if posture_rows else "NEEDS_MORE_DATA",
            f"Produced {len(posture_rows)} posture rows and route hints from accepted metadata.",
        ),
        _stage(
            "evidence_report",
            "PASS",
            "Generated a single evidence packet with boundaries, source artifacts, posture counts, and non-claims.",
        ),
    ]
    return {
        "version": VERSION,
        "generated_at": _now(),
        "source_name": SOURCE_NAME,
        "flow": [
            "metadata_intake",
            "schema_validation",
            "policy_evaluation",
            "posture_output",
            "evidence_report",
        ],
        "stage_results": stage_results,
        "policy": policy.decision_metadata(),
        "metadata_intake": {
            "input_action_count": intake_report["input_action_count"],
            "accepted_action_count": intake_report["accepted_action_count"],
            "classification_counts": intake_report["classification_counts"],
            "share_status": intake_report["share_status"],
        },
        "schema_validation": {
            "registry_count": schema_report["registry_count"],
            "tool_call_count": schema_report["tool_call_count"],
            "classification_counts": schema_report["classification_counts"],
            "smerc_posture_counts": schema_report["smerc_posture_counts"],
        },
        "posture_output": {
            "posture_counts": dict(sorted(posture_counts.items())),
            "route_counts": dict(sorted(route_counts.items())),
            "rows": posture_rows,
        },
        "artifacts": {
            "metadata_intake_input": str(intake_path),
            "schema_gate_input": str(schema_gate_path),
            "policy_input": str(policy_path),
            "metadata_intake_report": "reports/local_shadow_intake_report.json",
            "schema_gate_report": "reports/dynamic_schema_gate_report.json",
        },
        "work_result_impact": {
            "work": (
                "Run one reviewer-facing proof path from local metadata intake through schema validation, policy "
                "identity, posture output, and evidence reporting."
            ),
            "result": (
                "SMERC can show a coherent end-to-end flow without live AWS credentials, raw logs, customer data, "
                "or production execution authority."
            ),
            "impact": (
                "A contributor can map AWS-like or tool-call actions into SMERC safely enough for public review, "
                "while a company reviewer can see the exact handoff points needed for a private shadow-mode pilot."
            ),
        },
        "evidence_boundary": (
            "This is a local proof wrapper. It does not call AWS, connect to MCP servers, execute tools, certify "
            "anonymization, prove incident reduction, or replace IAM, policy engines, scanners, approval workflows, "
            "SIEM, SOAR, or human accountability."
        ),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC End-to-End Reviewer Flow",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Version: `{report['version']}`",
        "",
        "## Flow",
        "",
        "`metadata intake -> schema validation -> policy evaluation -> posture output -> evidence report`",
        "",
        "## Work / Result / Impact",
        "",
        f"- Work: {report['work_result_impact']['work']}",
        f"- Result: {report['work_result_impact']['result']}",
        f"- Impact: {report['work_result_impact']['impact']}",
        "",
        "## Stage Results",
        "",
        "| Stage | Status | Summary |",
        "| --- | --- | --- |",
    ]
    for stage in report["stage_results"]:
        lines.append(f"| `{stage['stage']}` | `{stage['status']}` | {stage['summary']} |")
    lines.extend(
        [
            "",
            "## Policy Identity",
            "",
            f"- Policy: `{report['policy']['policy_id']}@{report['policy']['policy_revision']}`",
            f"- Mode: `{report['policy']['mode']}`",
            f"- Evidence ceiling: `{report['policy']['evidence_ceiling']}`",
            f"- Policy hash: `{report['policy']['policy_hash']}`",
            "",
            "## Summary",
            "",
            f"- Metadata actions accepted: `{report['metadata_intake']['accepted_action_count']}`",
            f"- Intake classifications: `{report['metadata_intake']['classification_counts']}`",
            f"- Schema classifications: `{report['schema_validation']['classification_counts']}`",
            f"- Posture counts: `{report['posture_output']['posture_counts']}`",
            f"- Route counts: `{report['posture_output']['route_counts']}`",
            "",
            "## Posture Rows",
            "",
            "| Action | Type | Tool class | Current handling | SMERC posture | Route | Evidence |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report["posture_output"]["rows"]:
        lines.append(
            f"| `{row['action_id']}` | `{row['action_type']}` | `{row['tool_system_class']}` | "
            f"`{row['current_system_posture']}` | `{row['smerc_posture']}` | `{row['route_hint']}` | "
            f"`{row['evidence_available']}` |"
        )
    lines.extend(["", "## Evidence Boundary", "", str(report["evidence_boundary"]), ""])
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], *, json_output: str | Path, markdown_output: str | Path) -> None:
    Path(json_output).parent.mkdir(parents=True, exist_ok=True)
    Path(markdown_output).parent.mkdir(parents=True, exist_ok=True)
    Path(json_output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(markdown_output).write_text(render_markdown(report), encoding="utf-8")


def _posture_row(action: Mapping[str, Any], policy: Mapping[str, str]) -> Dict[str, Any]:
    posture = action["intake_posture_hint"]
    return {
        "action_id": action["action_id"],
        "action_type": action["action_type"],
        "tool_system_class": action["tool_system_class"],
        "current_system_posture": action["current_system_posture"],
        "smerc_posture": posture,
        "route_hint": POSTURE_TO_ROUTE[posture],
        "evidence_available": action["evidence_available"],
        "rollback_latency_seconds": action["rollback_latency_seconds"],
        "containment_strength": action["containment_strength"],
        "policy_hash": policy["policy_hash"],
    }


def _stage(stage: str, status: str, summary: str) -> Dict[str, str]:
    return {"stage": stage, "status": status, "summary": summary}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the SMERC end-to-end reviewer flow proof.")
    parser.add_argument("--intake", default="examples/local_shadow_intake_examples.json")
    parser.add_argument("--schema-gate", default="examples/dynamic_schema_gate_examples.json")
    parser.add_argument("--policy", default="examples/policies/github_actions_shadow_spl.json")
    parser.add_argument("--json-output", default="reports/end_to_end_reviewer_flow.json")
    parser.add_argument("--markdown-output", default="reports/End_To_End_Reviewer_Flow.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_flow_report(intake_path=args.intake, schema_gate_path=args.schema_gate, policy_path=args.policy)
    write_outputs(report, json_output=args.json_output, markdown_output=args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
