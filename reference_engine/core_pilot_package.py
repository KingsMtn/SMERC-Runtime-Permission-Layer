from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from reference_engine.customer_action_intake import (
    evaluate_customer_intake,
    load_payload as load_customer_intake,
    render_markdown as render_customer_intake_markdown,
)
from reference_engine.pilot_evidence_summary import (
    build_summary,
    load_json,
    render_markdown as render_summary_markdown,
)
from reference_engine.prospect_router import (
    load_payload as load_prospect_route,
    render_markdown as render_prospect_route_markdown,
    route_prospect,
)


VERSION = "smerc.core-pilot-package.v1"


def build_core_pilot_package(
    *,
    prospect_route: str | Path = "examples/core_prospect_route_sample.json",
    customer_intake: str | Path = "examples/customer_action_intake_sample.json",
    pilot_handoff: str | Path = "examples/pilot_handoff_checklist.json",
    pilot_metrics: Optional[str | Path] = None,
) -> Dict[str, Any]:
    route_report = route_prospect(load_prospect_route(prospect_route))
    intake_report = evaluate_customer_intake(load_customer_intake(customer_intake))
    handoff = load_json(pilot_handoff)
    metrics = load_json(pilot_metrics) if pilot_metrics else None
    summary = build_summary(route_report, intake_report, handoff, pilot_metrics=metrics)
    return {
        "schema": VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "organization": summary["organization"],
        "route": summary["recommended_route"],
        "pilot_decision": summary["pilot_decision"],
        "package_artifacts": {
            "prospect_route": "prospect-route.json",
            "prospect_route_markdown": "prospect-route.md",
            "customer_action_intake": "customer-action-intake.json",
            "customer_action_intake_markdown": "customer-action-intake.md",
            "pilot_handoff": "pilot-handoff.json",
            "pilot_evidence_summary": "pilot-evidence-summary.json",
            "pilot_evidence_summary_markdown": "pilot-evidence-summary.md",
            "executive_index": "README.md",
        },
        "reports": {
            "prospect_route": route_report,
            "customer_action_intake": intake_report,
            "pilot_handoff": handoff,
            "pilot_metrics": metrics,
            "pilot_evidence_summary": summary,
        },
        "review_order": [
            "README.md",
            "prospect-route.md",
            "customer-action-intake.md",
            "pilot-evidence-summary.md",
            "pilot-handoff.json",
        ],
        "evidence_boundary": (
            "Core pilot package only. It is not production certification, compliance attestation, "
            "customer demand proof, incident-reduction proof, or approval for enforcement."
        ),
    }


def render_index(package: Mapping[str, Any]) -> str:
    summary = package["reports"]["pilot_evidence_summary"]
    lines = [
        "# SMERC Core Pilot Package",
        "",
        f"- Organization: `{package.get('organization')}`",
        f"- Generated: `{package.get('generated_at')}`",
        f"- Route: `{package.get('route')}`",
        f"- Pilot decision: `{package.get('pilot_decision')}`",
        "",
        "## Recommended Next Action",
        "",
        str(summary["recommended_next_action"]),
        "",
        "## Review Order",
        "",
    ]
    lines.extend(f"{index}. `{item}`" for index, item in enumerate(package["review_order"], start=1))
    lines.extend(
        [
            "",
            "## What This Package Includes",
            "",
            "- Prospect route: chooses core GitHub Actions, SMERC-F financial, or review-only path.",
            "- Customer action intake: scores metadata-only action examples.",
            "- Pilot handoff: checks owner, reviewer, boundary, stop-condition, and metric readiness.",
            "- Pilot evidence summary: makes the go/no-go style recommendation.",
            "",
            "## Evidence Boundary",
            "",
            str(package["evidence_boundary"]),
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(package: Mapping[str, Any], output_dir: str | Path) -> Dict[str, str]:
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    route = package["reports"]["prospect_route"]
    intake = package["reports"]["customer_action_intake"]
    handoff = package["reports"]["pilot_handoff"]
    summary = package["reports"]["pilot_evidence_summary"]
    files = {
        "README.md": render_index(package),
        "core-pilot-package.json": json.dumps(package, indent=2, sort_keys=True) + "\n",
        "prospect-route.json": json.dumps(route, indent=2, sort_keys=True) + "\n",
        "prospect-route.md": render_prospect_route_markdown(route),
        "customer-action-intake.json": json.dumps(intake, indent=2, sort_keys=True) + "\n",
        "customer-action-intake.md": render_customer_intake_markdown(intake),
        "pilot-handoff.json": json.dumps(handoff, indent=2, sort_keys=True) + "\n",
        "pilot-evidence-summary.json": json.dumps(summary, indent=2, sort_keys=True) + "\n",
        "pilot-evidence-summary.md": render_summary_markdown(summary),
    }
    written: Dict[str, str] = {}
    for name, content in files.items():
        path = target / name
        path.write_text(content, encoding="utf-8")
        written[name] = path.as_posix()
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the SMERC core pilot package.")
    parser.add_argument("--prospect-route", default="examples/core_prospect_route_sample.json")
    parser.add_argument("--customer-intake", default="examples/customer_action_intake_sample.json")
    parser.add_argument("--pilot-handoff", default="examples/pilot_handoff_checklist.json")
    parser.add_argument("--pilot-metrics")
    parser.add_argument("--output-dir", default="reports/core_pilot_package")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    package = build_core_pilot_package(
        prospect_route=args.prospect_route,
        customer_intake=args.customer_intake,
        pilot_handoff=args.pilot_handoff,
        pilot_metrics=args.pilot_metrics,
    )
    written = write_outputs(package, args.output_dir)
    response = {"package": package, "written": written}
    print(json.dumps(response, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
