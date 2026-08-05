from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from reference_engine.customer_action_intake import evaluate_customer_intake
from reference_engine.prospect_router import route_prospect


VERSION = "smerc.customer-metadata-validation.v1"
CHECKLIST_VERSION = "smerc.customer-metadata-substitution-checklist.v1"
SAMPLE_ORGANIZATIONS = {
    "ExampleCo",
    "Example Platform Team",
    "Example Stablecoin Infrastructure Team",
}


def load_json(path: str | Path) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return payload


def _as_route_report(payload: Mapping[str, Any]) -> Dict[str, Any]:
    if "recommended_route" in payload:
        return dict(payload)
    return route_prospect(payload)


def _as_intake_report(payload: Mapping[str, Any]) -> Dict[str, Any]:
    if "summary" in payload and "pilot_fit" in payload:
        return dict(payload)
    return evaluate_customer_intake(payload)


def _confirmations(checklist: Mapping[str, Any]) -> tuple[int, int, list[str]]:
    if checklist.get("schema") != CHECKLIST_VERSION:
        raise ValueError(f"checklist schema must be {CHECKLIST_VERSION}")
    items = checklist.get("required_confirmations")
    if not isinstance(items, list) or not items:
        raise ValueError("checklist.required_confirmations must be a non-empty list")
    confirmed = 0
    missing: list[str] = []
    for index, item in enumerate(items):
        if not isinstance(item, Mapping):
            raise TypeError(f"required_confirmations[{index}] must be an object")
        name = item.get("item")
        if not isinstance(name, str) or not name.strip():
            raise TypeError(f"required_confirmations[{index}].item must be a non-empty string")
        if item.get("required") is True and item.get("confirmed") is True:
            confirmed += 1
        elif item.get("required") is True:
            missing.append(name)
    return confirmed, len([item for item in items if isinstance(item, Mapping) and item.get("required") is True]), missing


def validate_customer_metadata(
    *,
    checklist: Mapping[str, Any],
    prospect_route: Mapping[str, Any],
    customer_intake: Mapping[str, Any],
    pilot_handoff: Mapping[str, Any],
    pilot_metrics: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    route_report = _as_route_report(prospect_route)
    intake_report = _as_intake_report(customer_intake)
    confirmed_count, required_count, unconfirmed = _confirmations(checklist)
    blockers = [f"Required substitution confirmation is not complete: {item}" for item in unconfirmed]
    organization = str(route_report.get("organization") or intake_report.get("organization") or "")
    intake_organization = str(intake_report.get("organization") or "")
    if organization in SAMPLE_ORGANIZATIONS or intake_organization in SAMPLE_ORGANIZATIONS:
        blockers.append("Public sample organization names are still present.")
    action_count = int(intake_report.get("summary", {}).get("total_actions") or 0)
    if action_count < 10:
        blockers.append("Customer action intake should include at least 10 metadata-only actions for a prospect package.")
    if action_count > 25:
        blockers.append("Customer action intake should include at most 25 actions for the first prospect package.")
    if route_report.get("recommended_route") == "review_only":
        blockers.append("Prospect route is review_only, so a pilot package should not be offered yet.")
    if pilot_handoff.get("schema") != "smerc.pilot-handoff-checklist.v1":
        blockers.append("Pilot handoff checklist schema is missing or invalid.")
    if pilot_metrics and "Sample pilot metrics" in str(pilot_metrics.get("interpretation_warning", "")):
        blockers.append("Sample pilot metrics are still present and must not be used as customer evidence.")

    ready = not blockers
    return {
        "schema": VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "organization": organization or intake_organization,
        "ready_for_customer_package": ready,
        "confirmation_status": {
            "confirmed_required_items": confirmed_count,
            "required_items": required_count,
            "unconfirmed_items": unconfirmed,
        },
        "route": route_report.get("recommended_route"),
        "pilot_fit": intake_report.get("pilot_fit", {}).get("fit"),
        "action_count": action_count,
        "blockers": blockers,
        "recommended_next_action": (
            "Generate the customer-specific core pilot package."
            if ready
            else "Resolve every blocker before sending or relying on a prospect-specific pilot package."
        ),
        "evidence_boundary": (
            "Customer metadata validation only. It does not prove customer demand, pilot success, "
            "production safety, incident reduction, compliance, or approval for enforcement."
        ),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC Customer Metadata Validation Report",
        "",
        f"- Organization: `{report.get('organization')}`",
        f"- Generated: `{report.get('generated_at')}`",
        f"- Ready for customer package: `{str(report.get('ready_for_customer_package')).lower()}`",
        f"- Route: `{report.get('route')}`",
        f"- Pilot fit: `{report.get('pilot_fit')}`",
        f"- Action count: `{report.get('action_count')}`",
        "",
        "## Confirmation Status",
        "",
        f"- Confirmed required items: `{report['confirmation_status']['confirmed_required_items']}` of `{report['confirmation_status']['required_items']}`",
        "",
        "## Blockers",
        "",
    ]
    if report["blockers"]:
        lines.extend(f"- {item}" for item in report["blockers"])
    else:
        lines.append("- None identified by this validation screen.")
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
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate customer metadata substitution before generating a SMERC pilot package.")
    parser.add_argument("--checklist", default="examples/customer_metadata_substitution_checklist.json")
    parser.add_argument("--prospect-route", default="examples/core_prospect_route_sample.json")
    parser.add_argument("--customer-intake", default="examples/customer_action_intake_sample.json")
    parser.add_argument("--pilot-handoff", default="examples/pilot_handoff_checklist.json")
    parser.add_argument("--pilot-metrics")
    parser.add_argument("--json-output", default="reports/customer_metadata_validation_report.json")
    parser.add_argument("--markdown-output", default="reports/Customer_Metadata_Validation_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = validate_customer_metadata(
        checklist=load_json(args.checklist),
        prospect_route=load_json(args.prospect_route),
        customer_intake=load_json(args.customer_intake),
        pilot_handoff=load_json(args.pilot_handoff),
        pilot_metrics=load_json(args.pilot_metrics) if args.pilot_metrics else None,
    )
    write_outputs(report, args.json_output, args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
