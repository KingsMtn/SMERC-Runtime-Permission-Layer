from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping


VERSION = "smerc.prospect-route.v1"
WORKFLOW_SIGNAL_FIELDS = {
    "ai_agent_or_automation_actions",
    "github_actions_or_ci_cd_workflow",
    "financial_or_stablecoin_workflow",
    "side_effecting_actions",
    "meaningful_irreversible_exposure",
    "metadata_only_intake_possible",
    "reviewer_labels_possible",
    "observe_mode_possible",
    "live_fund_movement_required_for_first_test",
    "expects_aml_compliance_replacement",
    "expects_production_blocking_first",
}


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    return value.strip()


def _bool(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{path} must be a boolean")
    return value


def validate_payload(payload: Mapping[str, Any]) -> Dict[str, Any]:
    required = {
        "schema",
        "organization",
        "assessment_date",
        "organization_type",
        "primary_buyer",
        "technical_owner",
        "workflow_signals",
        "evidence",
    }
    missing = sorted(required - set(payload))
    unknown = sorted(set(payload) - required)
    if missing:
        raise ValueError(f"prospect route payload is missing field(s): {', '.join(missing)}")
    if unknown:
        raise ValueError(f"prospect route payload contains unknown field(s): {', '.join(unknown)}")
    if payload["schema"] != VERSION:
        raise ValueError(f"schema must be {VERSION}")
    signals = payload["workflow_signals"]
    if not isinstance(signals, dict):
        raise TypeError("workflow_signals must be an object")
    signal_missing = sorted(WORKFLOW_SIGNAL_FIELDS - set(signals))
    signal_unknown = sorted(set(signals) - WORKFLOW_SIGNAL_FIELDS)
    if signal_missing:
        raise ValueError(f"workflow_signals missing field(s): {', '.join(signal_missing)}")
    if signal_unknown:
        raise ValueError(f"workflow_signals contains unknown field(s): {', '.join(signal_unknown)}")
    evidence = payload["evidence"]
    if not isinstance(evidence, dict):
        raise TypeError("evidence must be an object")
    return {
        "schema": VERSION,
        "organization": _text(payload["organization"], "organization"),
        "assessment_date": _text(payload["assessment_date"], "assessment_date"),
        "organization_type": _text(payload["organization_type"], "organization_type"),
        "primary_buyer": _text(payload["primary_buyer"], "primary_buyer"),
        "technical_owner": _text(payload["technical_owner"], "technical_owner"),
        "workflow_signals": {field: _bool(signals[field], f"workflow_signals.{field}") for field in WORKFLOW_SIGNAL_FIELDS},
        "evidence": {str(key): _text(value, f"evidence.{key}") for key, value in evidence.items()},
    }


def route_prospect(payload: Mapping[str, Any]) -> Dict[str, Any]:
    parsed = validate_payload(payload)
    signals = parsed["workflow_signals"]
    blockers = blockers_for(signals)
    core_score = score_core(signals)
    financial_score = score_financial(signals)
    if blockers:
        route = "review_only"
        next_action = "Do not offer a paid pilot. Share public review materials and ask for safer metadata, reviewer ownership, or observe-mode feasibility."
    elif financial_score > core_score and financial_score >= 5:
        route = "smerc_f_financial_shadow_mode"
        next_action = "Use the SMERC-F financial shadow-mode pilot path with metadata-only action examples and no live fund movement."
    elif core_score >= 5:
        route = "core_github_actions_shadow_mode"
        next_action = "Use the core GitHub Actions shadow-mode pilot path with customer action intake and pilot handoff checklist."
    else:
        route = "review_only"
        next_action = "Start with reviewer quickstart and customer action intake before discussing a pilot."
    return {
        "schema": VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "organization": parsed["organization"],
        "organization_type": parsed["organization_type"],
        "primary_buyer": parsed["primary_buyer"],
        "technical_owner": parsed["technical_owner"],
        "recommended_route": route,
        "core_github_actions_score": core_score,
        "smerc_f_financial_score": financial_score,
        "blockers": blockers,
        "next_action": next_action,
        "recommended_materials": materials_for(route),
        "evidence": parsed["evidence"],
        "evidence_boundary": "Prospect routing screen only. It is not proof of buyer intent, customer demand, pilot success, AML compliance, production readiness, or incident reduction.",
    }


def blockers_for(signals: Mapping[str, bool]) -> list[str]:
    blockers: list[str] = []
    if not signals["ai_agent_or_automation_actions"]:
        blockers.append("No AI-agent or automation action surface identified.")
    if not signals["side_effecting_actions"]:
        blockers.append("No meaningful side-effecting action surface identified.")
    if not signals["metadata_only_intake_possible"]:
        blockers.append("Metadata-only intake is not possible.")
    if not signals["reviewer_labels_possible"]:
        blockers.append("Reviewer labels are not available.")
    if not signals["observe_mode_possible"]:
        blockers.append("Observe mode is not possible.")
    if signals["expects_production_blocking_first"]:
        blockers.append("Prospect expects production blocking before shadow-mode evidence.")
    if signals["expects_aml_compliance_replacement"]:
        blockers.append("Prospect expects SMERC-F to replace AML compliance.")
    if signals["live_fund_movement_required_for_first_test"]:
        blockers.append("Prospect requires live fund movement for the first financial test.")
    return blockers


def score_core(signals: Mapping[str, bool]) -> int:
    return sum(
        1
        for field in (
            "ai_agent_or_automation_actions",
            "github_actions_or_ci_cd_workflow",
            "side_effecting_actions",
            "meaningful_irreversible_exposure",
            "metadata_only_intake_possible",
            "reviewer_labels_possible",
            "observe_mode_possible",
        )
        if signals[field]
    )


def score_financial(signals: Mapping[str, bool]) -> int:
    return sum(
        1
        for field in (
            "ai_agent_or_automation_actions",
            "financial_or_stablecoin_workflow",
            "side_effecting_actions",
            "meaningful_irreversible_exposure",
            "metadata_only_intake_possible",
            "reviewer_labels_possible",
            "observe_mode_possible",
        )
        if signals[field]
    )


def materials_for(route: str) -> list[str]:
    if route == "smerc_f_financial_shadow_mode":
        return [
            "docs/SMERC_F_AML_Inspired_Spur.md",
            "docs/SMERC_F_Stablecoin_Blockchain_Pilot_Fit.md",
            "pilot_package/SMERC_F_Financial_Shadow_Mode_Pilot_Path.md",
            "reports/AML_Inspired_Financial_Governance_Benchmark.md",
        ]
    if route == "core_github_actions_shadow_mode":
        return [
            "docs/Reviewer_Quickstart.md",
            "docs/Customer_Action_Intake.md",
            "pilot_package/First_Pilot_Path.md",
            "pilot_package/Pilot_Handoff_Checklist.md",
        ]
    return [
        "docs/External_Review_Start_Here.md",
        "docs/Reviewer_Quickstart.md",
        "docs/Customer_Action_Intake.md",
    ]


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        f"# {report['organization']} Prospect Route",
        "",
        f"Generated at: `{report['generated_at']}`",
        "",
        "## Recommendation",
        "",
        f"- Route: `{report['recommended_route']}`",
        f"- Core GitHub Actions score: `{report['core_github_actions_score']}`",
        f"- SMERC-F financial score: `{report['smerc_f_financial_score']}`",
        f"- Next action: {report['next_action']}",
        "",
        "## Blockers",
        "",
    ]
    if report["blockers"]:
        lines.extend(f"- {blocker}" for blocker in report["blockers"])
    else:
        lines.append("- None identified by this routing screen.")
    lines.extend(["", "## Recommended Materials", ""])
    lines.extend(f"- `{item}`" for item in report["recommended_materials"])
    lines.extend(["", "## Evidence Boundary", "", str(report["evidence_boundary"]), ""])
    return "\n".join(lines)


def load_payload(path: str | Path) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("prospect route file must contain a JSON object")
    return payload


def write_outputs(report: Mapping[str, Any], json_output: str | Path, markdown_output: str | Path) -> None:
    json_path = Path(json_output)
    markdown_path = Path(markdown_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Route a SMERC prospect to the right review or pilot path.")
    parser.add_argument("path", help="Path to smerc.prospect-route.v1 JSON.")
    parser.add_argument("--json-output", default="reports/prospect_route_report.json")
    parser.add_argument("--markdown-output", default="reports/Prospect_Route_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = route_prospect(load_payload(args.path))
    write_outputs(report, args.json_output, args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
