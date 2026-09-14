from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.complete_lifecycle_proof import build_complete_lifecycle_proof, load_json


VERSION = "smerc.whole-system-demo.v1"

EVIDENCE_BOUNDARY = (
    "This is a deterministic, metadata-only whole-system demo. It does not execute production commands, "
    "connect to AWS, GitHub, MCP servers, Linux Foundation projects, TRACE runtimes, or customer systems, "
    "prove production safety, certify compliance, prove customer demand, or prove incident reduction."
)


def build_whole_system_demo(payload: Mapping[str, Any]) -> Dict[str, Any]:
    lifecycle = build_complete_lifecycle_proof(payload)
    summary = lifecycle["summary"]
    stages = [
        _stage(
            "identity_context",
            "Identity / Context",
            "Validates actor, session, typed contract, attestation, least privilege, object shape, and required evidence before scoring.",
            lifecycle["runtime_admission"]["decision"],
            {
                "request_id": lifecycle["runtime_admission"]["request_id"],
                "missing_required_checks": lifecycle["runtime_admission"]["missing_required_checks"],
                "failed_required_checks": lifecycle["runtime_admission"]["failed_required_checks"],
            },
        ),
        _stage(
            "recoverability_engine",
            "Recoverability Engine",
            "Scores whether the proposed action is reversible, bounded, observable, and safe enough to proceed.",
            lifecycle["initial_decision"]["posture"],
            {
                "action_id": lifecycle["initial_decision"]["action_id"],
                "scores": lifecycle["initial_decision"]["scores"],
                "reason_codes": lifecycle["initial_decision"]["reason_codes"],
            },
        ),
        _stage(
            "decision_posture",
            "Decision Posture",
            "Converts recoverability judgment into the shared SMERC decision language.",
            lifecycle["initial_decision"]["posture"],
            {
                "posture": lifecycle["initial_decision"]["posture"],
                "enforcement_state": lifecycle["initial_decision"]["enforcement_state"],
                "controls": lifecycle["initial_decision"]["controls"],
            },
        ),
        _stage(
            "sparta_route",
            "SPARTa Route Controls",
            "Translates posture into execution routing, required controls, and whether the action can execute.",
            lifecycle["initial_sparta_route"]["route_state"],
            {
                "route_state": lifecycle["initial_sparta_route"]["route_state"],
                "executable": lifecycle["initial_sparta_route"]["executable"],
                "applied_controls": lifecycle["initial_sparta_route"]["applied_controls"],
            },
        ),
        _stage(
            "recovery_authority",
            "Recovery Authority Gate",
            "Requires separate authority and fresh recovery evidence before a paused action can continue.",
            lifecycle["recovery_authority_gate"]["recovery_authority"]["state"],
            {
                "unlock_actor": lifecycle["recovery_authority_gate"]["unlock_actor"]["actor_id"],
                "drivers": lifecycle["recovery_authority_gate"]["recovery_authority"]["drivers"],
            },
        ),
        _stage(
            "continuation_route",
            "Bounded Continuation",
            "Re-scores the narrowed continuation action and routes it through constrained execution.",
            summary["continuation_route"],
            {
                "continuation_posture": summary["continuation_posture"],
                "continuation_route": summary["continuation_route"],
                "continuation_controls": lifecycle["continuation_sparta_route"]["applied_controls"]
                if lifecycle["continuation_sparta_route"]
                else [],
            },
        ),
        _stage(
            "executor_gateway",
            "Executor / Gateway",
            "Executes only the permitted bounded route, using a short-lived action-bound permit.",
            lifecycle["execution_result"]["execution_status"],
            {
                "permit_issued": summary["permit_issued"],
                "permit_verified": summary["permit_verified"],
                "execution_status": lifecycle["execution_result"]["execution_status"],
                "executed_operation": lifecycle["execution_result"]["executed_operation"],
            },
        ),
        _stage(
            "postcondition_evidence",
            "Postcondition Evidence",
            "Records whether the required controls and execution result can be checked after the route.",
            lifecycle["execution_result"]["execution_status"],
            {
                "rollback_performed": lifecycle["execution_result"]["rollback_performed"],
                "rollback_success": lifecycle["execution_result"]["rollback_success"],
                "notes": lifecycle["execution_result"]["notes"],
            },
        ),
        _stage(
            "decision_lifecycle_ledger",
            "Decision Lifecycle Ledger",
            "Preserves a replayable chain of request, evidence, evaluation, human interaction, execution, outcome, and learning records.",
            "valid" if summary["ledger_valid"] else "invalid",
            {
                "decision_id": lifecycle["decision_lifecycle_ledger"]["decision_id"],
                "record_count": len(lifecycle["decision_lifecycle_ledger"]["records"]),
                "ledger_valid": summary["ledger_valid"],
            },
        ),
    ]
    status = "whole_system_complete" if summary["overall_status"] == "COMPLETE" and summary["ledger_valid"] else "review_required"
    return {
        "version": VERSION,
        "generated_at": _now(),
        "status": status,
        "source_lifecycle_version": lifecycle["version"],
        "tenant_id": lifecycle["tenant_id"],
        "one_line_summary": (
            "SMERC takes one proposed high-impact action from identity/context through recoverability scoring, "
            "posture, route controls, separate recovery authority, bounded execution, postcondition evidence, "
            "and a valid decision lifecycle ledger."
        ),
        "system_flow": [
            "Identity / Context",
            "Recoverability Engine",
            "Decision Posture",
            "SPARTa Route Controls",
            "Recovery Authority Gate",
            "Bounded Continuation",
            "Executor / Gateway",
            "Postcondition Evidence",
            "Decision Lifecycle Ledger",
        ],
        "stages": stages,
        "summary": {
            "overall_status": summary["overall_status"],
            "initial_posture": summary["initial_posture"],
            "initial_route": summary["initial_route"],
            "unlock_state": summary["unlock_state"],
            "continuation_posture": summary["continuation_posture"],
            "continuation_route": summary["continuation_route"],
            "execution_status": summary["execution_status"],
            "ledger_valid": summary["ledger_valid"],
        },
        "linked_proofs": {
            "complete_lifecycle_proof": "docs/Complete_Lifecycle_Proof.md",
            "aws_decision_api_surface": "docs/AWS_Decision_API_Surface.md",
            "trace_evidence_adapter": "docs/TRACE_Evidence_Adapter.md",
            "postcondition_evidence": "docs/Postcondition_Evidence.md",
            "customer_metadata_request": "docs/Customer_Owned_Metadata_Request.md",
        },
        "evidence_boundary": EVIDENCE_BOUNDARY,
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC Whole-System Demo",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Version: `{report['version']}`",
        f"Status: `{report['status']}`",
        "",
        "## One-Line Summary",
        "",
        str(report["one_line_summary"]),
        "",
        "## System Flow",
        "",
        "```text",
        "Identity / Context",
        "        -> Recoverability Engine",
        "        -> Decision Posture",
        "        -> SPARTa Route Controls",
        "        -> Recovery Authority Gate",
        "        -> Bounded Continuation",
        "        -> Executor / Gateway",
        "        -> Postcondition Evidence",
        "        -> Decision Lifecycle Ledger",
        "```",
        "",
        "## Stage Results",
        "",
        "| Stage | Role | Result |",
        "| --- | --- | --- |",
    ]
    for stage in report["stages"]:
        lines.append(f"| {stage['name']} | {stage['role']} | `{stage['result']}` |")
    lines.extend(
        [
            "",
            "## Summary",
            "",
        ]
    )
    for key, value in report["summary"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Linked Proofs",
            "",
        ]
    )
    for name, path in report["linked_proofs"].items():
        lines.append(f"- {name}: `{path}`")
    lines.extend(
        [
            "",
            "## Evidence Boundary",
            "",
            str(report["evidence_boundary"]),
            "",
            "## Work / Result / Impact",
            "",
            "- Work: show SMERC as one coordinated runtime safety system, not a pile of separate artifacts.",
            "- Result: one action moves from identity/context to recoverability, posture, route controls, bounded continuation, execution evidence, and ledger verification.",
            "- Impact: reviewers can understand the whole system before inspecting the deeper AWS, TRACE-style, postcondition, or customer-metadata proof paths.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], output_dir: str | Path) -> Dict[str, str]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "whole_system_demo.json"
    markdown_path = out / "Whole_System_Demo.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(markdown_path)}


def _stage(stage_id: str, name: str, role: str, result: str, evidence: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "stage_id": stage_id,
        "name": name,
        "role": role,
        "result": str(result),
        "evidence": dict(evidence),
    }


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the SMERC whole-system demo.")
    parser.add_argument("--case", default="examples/complete_lifecycle/lifecycle_case.json")
    parser.add_argument("--output-dir", default="reports/whole_system_demo")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_whole_system_demo(load_json(args.case))
    paths = write_outputs(report, args.output_dir)
    stdout = {"summary": report["summary"], "written": paths}
    if args.pretty:
        stdout["report"] = report
    print(json.dumps(stdout, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
