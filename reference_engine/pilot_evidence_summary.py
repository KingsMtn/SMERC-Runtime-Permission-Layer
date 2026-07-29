from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional


VERSION = "smerc.pilot-evidence-summary.v1"


def load_json(path: str | Path) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return payload


def _count_yes_required_items(handoff: Mapping[str, Any]) -> tuple[int, int]:
    items = handoff.get("required_items", [])
    if not isinstance(items, list) or not items:
        return 0, 0
    yes = 0
    for item in items:
        if isinstance(item, Mapping) and item.get("status") == "yes":
            yes += 1
    return yes, len(items)


def _metric(metrics: Optional[Mapping[str, Any]], name: str) -> Any:
    if not metrics:
        return None
    values = metrics.get("metrics", {})
    if not isinstance(values, Mapping):
        return None
    return values.get(name)


def _decision(prospect_route: str, pilot_fit: str, handoff_yes: int, handoff_total: int, metrics: Optional[Mapping[str, Any]]) -> str:
    if prospect_route == "review_only":
        return "review_only"
    if pilot_fit == "weak":
        return "stop"
    if handoff_total == 0 or handoff_yes < handoff_total:
        return "not_ready_for_observe"
    agreement = _metric(metrics, "reviewer_agreement_rate")
    false_release = _metric(metrics, "false_release_rate")
    false_constraint = _metric(metrics, "false_constraint_rate")
    if agreement is None:
        return "start_observe"
    if false_release is not None and false_release > 0.05:
        return "narrow"
    if false_constraint is not None and false_constraint > 0.25:
        return "narrow"
    if agreement >= 0.75:
        return "move_to_recommend"
    return "continue_observe"


def build_summary(
    prospect_route: Mapping[str, Any],
    customer_intake: Mapping[str, Any],
    pilot_handoff: Mapping[str, Any],
    *,
    pilot_metrics: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    handoff_yes, handoff_total = _count_yes_required_items(pilot_handoff)
    route = str(prospect_route.get("recommended_route", "review_only"))
    pilot_fit = str(customer_intake.get("pilot_fit", {}).get("fit", "weak"))
    decision = _decision(route, pilot_fit, handoff_yes, handoff_total, pilot_metrics)
    intake_summary = customer_intake.get("summary", {})
    return {
        "schema": VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "organization": prospect_route.get("organization") or customer_intake.get("organization"),
        "recommended_route": route,
        "pilot_fit": pilot_fit,
        "pilot_decision": decision,
        "prospect_scores": {
            "core_github_actions_score": prospect_route.get("core_github_actions_score"),
            "smerc_f_financial_score": prospect_route.get("smerc_f_financial_score"),
        },
        "handoff_gate": {
            "yes_count": handoff_yes,
            "required_count": handoff_total,
            "complete": handoff_total > 0 and handoff_yes == handoff_total,
        },
        "action_intake_summary": {
            "total_actions": intake_summary.get("total_actions"),
            "posture_counts": intake_summary.get("posture_counts"),
            "highest_exposure_actions": intake_summary.get("highest_exposure_actions"),
            "actions_with_metadata_notes": intake_summary.get("actions_with_metadata_notes"),
        },
        "pilot_metrics_summary": summarize_metrics(pilot_metrics),
        "go_no_go_options": ["stop", "narrow", "continue_observe", "move_to_recommend"],
        "recommended_next_action": next_action_for(decision),
        "evidence_inputs": {
            "prospect_route_schema": prospect_route.get("schema"),
            "customer_intake_schema": customer_intake.get("schema"),
            "pilot_handoff_schema": pilot_handoff.get("schema"),
            "pilot_metrics_status": pilot_metrics.get("evidence_status") if pilot_metrics else "not_supplied",
        },
        "evidence_boundary": (
            "Pilot evidence summary only. It is not production certification, compliance attestation, "
            "customer demand proof, incident-reduction proof, or approval for enforcement."
        ),
    }


def summarize_metrics(pilot_metrics: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    if not pilot_metrics:
        return {
            "status": "not_supplied",
            "meaning": "No reviewer-labeled pilot metrics were supplied. The package can support observe-mode start, not post-pilot claims.",
        }
    return {
        "status": str(pilot_metrics.get("evidence_status", "supplied")),
        "decision_count": pilot_metrics.get("decision_count"),
        "reviewed_decision_count": pilot_metrics.get("reviewed_decision_count"),
        "reviewer_agreement_rate": _metric(pilot_metrics, "reviewer_agreement_rate"),
        "override_rate": _metric(pilot_metrics, "override_rate"),
        "false_release_rate": _metric(pilot_metrics, "false_release_rate"),
        "false_constraint_rate": _metric(pilot_metrics, "false_constraint_rate"),
        "useful_constraint_rate": _metric(pilot_metrics, "useful_constraint_rate"),
        "average_review_latency_ms": _metric(pilot_metrics, "average_review_latency_ms"),
        "interpretation_warning": pilot_metrics.get("interpretation_warning"),
    }


def next_action_for(decision: str) -> str:
    return {
        "review_only": "Do not offer a pilot yet. Send public review materials and ask for clearer workflow ownership, metadata boundary, and reviewer capacity.",
        "stop": "Stop or decline the pilot because the action intake does not show enough recoverability pain or pilot fit.",
        "not_ready_for_observe": "Complete the pilot handoff checklist before connecting any workflow.",
        "start_observe": "Start observe-mode scoring on one workflow and collect reviewer labels before making stronger claims.",
        "continue_observe": "Continue observe mode until reviewer agreement, false release, false constraint, and useful constraint metrics are more conclusive.",
        "narrow": "Narrow the workflow, thresholds, metadata boundary, or reviewer process before expanding.",
        "move_to_recommend": "Move to recommend mode only with customer owner approval; do not enforce yet.",
    }[decision]


def render_markdown(summary: Mapping[str, Any]) -> str:
    metrics = summary["pilot_metrics_summary"]
    intake = summary["action_intake_summary"]
    lines = [
        "# SMERC Pilot Evidence Summary",
        "",
        f"- Organization: `{summary.get('organization')}`",
        f"- Generated: `{summary.get('generated_at')}`",
        f"- Recommended route: `{summary.get('recommended_route')}`",
        f"- Pilot fit: `{summary.get('pilot_fit')}`",
        f"- Pilot decision: `{summary.get('pilot_decision')}`",
        "",
        "## Recommended Next Action",
        "",
        str(summary["recommended_next_action"]),
        "",
        "## Handoff Gate",
        "",
        f"- Complete: `{str(summary['handoff_gate']['complete']).lower()}`",
        f"- Required items yes: `{summary['handoff_gate']['yes_count']}` of `{summary['handoff_gate']['required_count']}`",
        "",
        "## Action Intake",
        "",
        f"- Total actions: `{intake.get('total_actions')}`",
        f"- Posture counts: `{intake.get('posture_counts')}`",
        f"- Actions with metadata notes: `{intake.get('actions_with_metadata_notes')}`",
        "",
        "## Pilot Metrics",
        "",
        f"- Status: `{metrics.get('status')}`",
        f"- Decisions: `{metrics.get('decision_count')}`",
        f"- Reviewed decisions: `{metrics.get('reviewed_decision_count')}`",
        f"- Reviewer agreement rate: `{metrics.get('reviewer_agreement_rate')}`",
        f"- False release rate: `{metrics.get('false_release_rate')}`",
        f"- False constraint rate: `{metrics.get('false_constraint_rate')}`",
        f"- Useful constraint rate: `{metrics.get('useful_constraint_rate')}`",
        f"- Average review latency ms: `{metrics.get('average_review_latency_ms')}`",
        "",
        "## Highest Exposure Actions",
        "",
        "| Action | Posture | Exposure | Capacity |",
        "| --- | --- | ---: | ---: |",
    ]
    for item in intake.get("highest_exposure_actions") or []:
        lines.append(
            f"| `{item.get('action_id')}` | `{item.get('posture')}` | {item.get('irreversible_exposure_score')} | {item.get('reversible_capacity_score')} |"
        )
    lines.extend(
        [
            "",
            "## Evidence Boundary",
            "",
            str(summary["evidence_boundary"]),
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(summary: Mapping[str, Any], json_output: str | Path, markdown_output: str | Path) -> None:
    json_path = Path(json_output)
    markdown_path = Path(markdown_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(summary), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a SMERC pilot evidence summary package.")
    parser.add_argument("--prospect-route", default="reports/prospect_route_report.json")
    parser.add_argument("--customer-intake", default="reports/customer_action_intake_report.json")
    parser.add_argument("--pilot-handoff", default="examples/pilot_handoff_checklist.json")
    parser.add_argument("--pilot-metrics")
    parser.add_argument("--json-output", default="reports/pilot_evidence_summary.json")
    parser.add_argument("--markdown-output", default="reports/Pilot_Evidence_Summary.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    summary = build_summary(
        load_json(args.prospect_route),
        load_json(args.customer_intake),
        load_json(args.pilot_handoff),
        pilot_metrics=load_json(args.pilot_metrics) if args.pilot_metrics else None,
    )
    write_outputs(summary, args.json_output, args.markdown_output)
    print(json.dumps(summary, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
