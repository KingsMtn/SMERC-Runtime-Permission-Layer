from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping


VERSION = "smerc.customer-owned-metadata-request.v1"

WORKFLOW_FAMILIES = {
    "general": [
        "AI-assisted code or deployment action",
        "MCP tool call",
        "support automation action",
        "security-response automation action",
    ],
    "cloud": [
        "IAM or permission change",
        "network boundary change",
        "database or storage action",
        "Kubernetes, DNS, capacity, or backup-policy action",
    ],
    "financial": [
        "payment retry or refund action",
        "treasury or liquidity movement",
        "stablecoin or tokenized-collateral action",
        "wallet-policy, transaction-limit, or reserve-status action",
    ],
}

REQUIRED_FIELDS = [
    "action_id",
    "action_description",
    "actor_or_agent_role",
    "tool_family",
    "environment",
    "requested_scope",
    "current_control_outcome",
    "base_action_risk",
    "reversibility",
    "containment_strength",
    "rollback_latency",
    "evidence_validity",
    "anomaly_pressure",
    "impact_scope",
    "cancel_reliability",
    "authorization_confidence",
    "typed_contract_present",
    "attestation_valid",
    "least_privilege_confirmed",
    "object_shape_valid",
]

EXCLUDED_DATA = [
    "secrets, API keys, tokens, passwords, private keys, or wallet keys",
    "source code bodies, private prompts, model prompts, or proprietary policies",
    "raw customer records, regulated transaction payloads, AML case files, or sanctions-screening records",
    "production logs, incident details, account numbers, or confidential infrastructure diagrams",
    "live credentials or authorization to execute production actions",
]


def build_request_report(*, workflow_family: str = "general", requested_actions: int = 10) -> Dict[str, Any]:
    if workflow_family not in WORKFLOW_FAMILIES:
        raise ValueError(f"workflow_family must be one of: {', '.join(sorted(WORKFLOW_FAMILIES))}")
    if requested_actions < 5 or requested_actions > 25:
        raise ValueError("requested_actions must be between 5 and 25")

    return {
        "version": VERSION,
        "generated_at": _now(),
        "workflow_family": workflow_family,
        "requested_action_count": requested_actions,
        "request": (
            f"Please replace the public examples with {requested_actions} metadata-only actions from one "
            f"{workflow_family} workflow family."
        ),
        "acceptable_action_types": WORKFLOW_FAMILIES[workflow_family],
        "required_fields": REQUIRED_FIELDS,
        "excluded_data": EXCLUDED_DATA,
        "commands": {
            "general_customer_evaluation": (
                "python -m reference_engine.customer_evaluation customer_working/customer_actions.json "
                "--json-output reports/customer_working/customer_evaluation_report.json "
                "--markdown-output reports/customer_working/Customer_Evaluation_Report.md --pretty"
            ),
            "validate_customer_metadata": (
                "python -m reference_engine.customer_metadata_validator "
                "--checklist customer_working/customer_metadata_substitution_checklist.json "
                "--prospect-route customer_working/prospect_route.json "
                "--customer-intake customer_working/customer_action_intake.json "
                "--pilot-handoff customer_working/pilot_handoff.json --pretty"
            ),
            "serious_report_performance": "python -m reference_engine.serious_report_performance --iterations 5 --pretty",
        },
        "reviewer_questions": [
            "Which SMERC posture matched current reviewer judgment?",
            "Which action was usefully constrained instead of simply allowed or blocked?",
            "Which action failed because evidence was missing or untrusted?",
            "Which p95 workflow overhead would make this unsuitable?",
            "Would these results justify a bounded shadow-mode pilot?",
        ],
        "work_result_impact": {
            "work": "Ask an external reviewer to supply safe metadata-only actions from one real workflow.",
            "result": (
                "SMERC can compare customer-owned action metadata against its public examples, posture logic, "
                "SPARTa routes, postcondition evidence expectations, and local performance metrics."
            ),
            "impact": (
                "The project can move from synthetic proof toward reviewer-owned evidence without requesting "
                "secrets, production access, regulated payloads, or enforcement authority."
            ),
        },
        "evidence_boundary": (
            "Customer-owned metadata review is still pre-production and shadow-mode. It does not prove "
            "customer demand, incident reduction, compliance, production safety, or enforce-mode readiness."
        ),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# Customer-Owned Metadata Request",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Version: `{report['version']}`",
        f"Workflow family: `{report['workflow_family']}`",
        f"Requested actions: `{report['requested_action_count']}`",
        "",
        "## Request",
        "",
        str(report["request"]),
        "",
        "## Acceptable Action Types",
        "",
    ]
    lines.extend(f"- {item}" for item in report["acceptable_action_types"])
    lines.extend(["", "## Required Metadata Fields", ""])
    lines.extend(f"- `{item}`" for item in report["required_fields"])
    lines.extend(["", "## Do Not Provide", ""])
    lines.extend(f"- {item}" for item in report["excluded_data"])
    lines.extend(
        [
            "",
            "## Commands",
            "",
            "```bash",
            report["commands"]["general_customer_evaluation"],
            "",
            report["commands"]["validate_customer_metadata"],
            "",
            report["commands"]["serious_report_performance"],
            "```",
            "",
            "## Reviewer Questions",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["reviewer_questions"])
    lines.extend(
        [
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


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a customer-owned metadata request for SMERC review.")
    parser.add_argument("--workflow-family", choices=sorted(WORKFLOW_FAMILIES), default="general")
    parser.add_argument("--requested-actions", type=int, default=10)
    parser.add_argument("--json-output", default="reports/customer_owned_metadata_request.json")
    parser.add_argument("--markdown-output", default="reports/Customer_Owned_Metadata_Request.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_request_report(workflow_family=args.workflow_family, requested_actions=args.requested_actions)
    write_outputs(report, json_path=args.json_output, markdown_path=args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
