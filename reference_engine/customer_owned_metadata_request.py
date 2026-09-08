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
    "aws": [
        "AgentCore Runtime or Gateway tool invocation",
        "IAM execution-role or permission-boundary change",
        "CloudFormation change-set or drift remediation action",
        "S3 policy, Secrets Manager rotation, RDS, cost-velocity, or cross-account delegation action",
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

AWS_RECOMMENDED_FIELDS = [
    "source_format",
    "aws_surface",
    "proposed_action_type",
    "service_family",
    "resource_class",
    "region_scope_count",
    "identity_scope_summary",
    "permission_boundary_present",
    "dry_run_or_preview_available",
    "change_set_or_plan_available",
    "checkpoint_available",
    "rollback_plan_available",
    "gateway_path_enforced",
    "direct_runtime_path_blocked",
    "cloudtrail_management_event_expected",
    "cloudtrail_data_event_expected",
    "cloudwatch_metric_or_log_expected",
    "agentcore_trace_or_span_expected",
    "runtime_usage_log_expected",
    "tool_result_metadata_expected",
    "estimated_cost_velocity",
    "cost_anomaly_signal_present",
]

EXCLUDED_DATA = [
    "secrets, API keys, tokens, passwords, private keys, or wallet keys",
    "source code bodies, private prompts, model prompts, or proprietary policies",
    "raw customer records, regulated transaction payloads, AML case files, or sanctions-screening records",
    "production logs, incident details, account numbers, or confidential infrastructure diagrams",
    "live credentials or authorization to execute production actions",
]

AWS_EXCLUDED_DATA = [
    "AWS account IDs, ARNs, access keys, session tokens, secret values, or credential material",
    "raw CloudTrail events, raw CloudWatch logs, raw trace bodies, private topology, or production commands",
    "customer records, regulated payloads, private prompts, proprietary policy bodies, or incident-sensitive details",
    "permission to assume roles, inspect live accounts, execute change sets, modify IAM, access S3, rotate secrets, or change cross-account trust",
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
            f"{_workflow_label(workflow_family)} workflow family."
        ),
        "acceptable_action_types": WORKFLOW_FAMILIES[workflow_family],
        "required_fields": REQUIRED_FIELDS,
        "aws_recommended_fields": AWS_RECOMMENDED_FIELDS if workflow_family == "aws" else [],
        "excluded_data": EXCLUDED_DATA + (AWS_EXCLUDED_DATA if workflow_family == "aws" else []),
        "commands": {
            "general_customer_evaluation": (
                "python -m reference_engine.customer_evaluation customer_working/customer_actions.json "
                "--json-output reports/customer_working/customer_evaluation_report.json "
                "--markdown-output reports/customer_working/Customer_Evaluation_Report.md --pretty"
            ),
            "aws_metadata_adapter": (
                "python -m reference_engine.aws_metadata_adapter customer_working/aws_source_exports.json "
                "--normalized-output reports/customer_working/aws_normalized_customer_actions.json "
                "--json-output reports/customer_working/aws_metadata_adapter_report.json "
                "--markdown-output reports/customer_working/AWS_Metadata_Adapter_Report.md "
                "--customer-json-output reports/customer_working/aws_customer_evaluation_report.json "
                "--customer-markdown-output reports/customer_working/AWS_Customer_Evaluation_Report.md --pretty"
            ),
            "aws_postcondition_evidence": (
                "python -m reference_engine.aws_postcondition_evidence "
                "--evaluation reports/customer_working/aws_customer_evaluation_report.json "
                "--observations customer_working/aws_postcondition_observations.json "
                "--json-output reports/customer_working/aws_postcondition_evidence_report.json "
                "--markdown-output reports/customer_working/AWS_Postcondition_Evidence_Report.md --pretty"
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
        "aws_reviewer_questions": _aws_reviewer_questions() if workflow_family == "aws" else [],
        "work_result_impact": {
            "work": _work_text(workflow_family),
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
    if report.get("aws_recommended_fields"):
        lines.extend(["", "## AWS Recommended Metadata Fields", ""])
        lines.extend(f"- `{item}`" for item in report["aws_recommended_fields"])
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
            report["commands"]["aws_metadata_adapter"] if report["workflow_family"] == "aws" else "",
            "",
            report["commands"]["aws_postcondition_evidence"] if report["workflow_family"] == "aws" else "",
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
    if report.get("aws_reviewer_questions"):
        lines.extend(["", "## AWS Reviewer Questions", ""])
        lines.extend(f"- {item}" for item in report["aws_reviewer_questions"])
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


def _work_text(workflow_family: str) -> str:
    if workflow_family == "aws":
        return (
            "Ask an AWS-style platform reviewer to supply safe metadata-only action summaries and matching "
            "postcondition observation summaries from one real workflow."
        )
    return "Ask an external reviewer to supply safe metadata-only actions from one real workflow."


def _workflow_label(workflow_family: str) -> str:
    if workflow_family == "aws":
        return "AWS-style cloud automation"
    return workflow_family


def _aws_reviewer_questions() -> list[str]:
    return [
        "Can these AWS-style actions be reviewed without account IDs, ARNs, raw logs, secrets, or live access?",
        "Which action should be constrained instead of allowed or blocked outright?",
        "Which postcondition evidence source would prove the required control happened?",
        "Which control is hardest to prove: preview, scope limit, checkpoint, rollback plan, gateway enforcement, block, replay, or cost-velocity bound?",
        "Would these results justify a bounded AWS shadow-mode pilot where existing AWS/customer controls remain authoritative?",
    ]


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
