from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from reference_engine.postcondition_evidence import build_postcondition_report


VERSION = "smerc.aws-postcondition-evidence.v1"

AWS_EVIDENCE_SOURCES = {
    "agentcore_gateway_cloudtrail_management_event",
    "agentcore_gateway_cloudtrail_data_event",
    "agentcore_gateway_mcp_log",
    "agentcore_runtime_cloudwatch_metric",
    "agentcore_runtime_usage_log",
    "agentcore_runtime_trace_span",
    "cloudformation_change_set_record",
    "cloudtrail_management_event",
    "cloudwatch_metric_or_log",
    "cost_anomaly_signal",
    "iam_access_analyzer_or_policy_record",
    "s3_policy_audit_record",
    "secrets_rotation_record",
    "tool_result_metadata_stream",
}

PROHIBITED_FIELDS = {
    "account_id",
    "access_key",
    "arn",
    "aws_secret_access_key",
    "credential",
    "credentials",
    "customer_record",
    "private_topology",
    "production_command",
    "raw_cloudtrail_event",
    "raw_log",
    "secret",
    "session_token",
}

EXECUTION_STATUSES = {"succeeded", "failed", "not_executed", "held_for_review", "rolled_back"}
CONTROL_OUTCOMES = {"applied", "failed", "missing", "not_applicable"}


def load_aws_observations(path: str | Path) -> list[Dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError("AWS postcondition observations must be a non-empty JSON array")
    rows: list[Dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise TypeError(f"observations[{index}] must be an object")
        _reject_prohibited_fields(item, f"observations[{index}]")
        action_id = _text(item.get("action_id"), f"observations[{index}].action_id")
        if action_id in seen:
            raise ValueError(f"duplicate observation action_id: {action_id}")
        seen.add(action_id)
        rows.append(_normalize_aws_observation(item, index))
    return rows


def load_json_object(path: str | Path) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return payload


def build_aws_postcondition_report(
    evaluation: Mapping[str, Any], observations: Iterable[Mapping[str, Any]]
) -> Dict[str, Any]:
    normalized_observations = [dict(item) for item in observations]
    generic_report = build_postcondition_report(
        evaluation,
        [_to_generic_observation(item) for item in normalized_observations],
    )
    aws_by_action = {item["action_id"]: item for item in normalized_observations}

    records = []
    source_counts: Counter[str] = Counter()
    missing_source_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    for generic in generic_report["records"]:
        action_id = generic["action_id"]
        aws_observation = aws_by_action.get(action_id)
        aws_sources = []
        expected_sources = []
        missing_sources = []
        surface = "unobserved"
        if aws_observation:
            surface = aws_observation["aws_surface"]
            expected_sources = list(aws_observation["expected_aws_evidence_sources"])
            aws_sources = sorted(
                {
                    source
                    for control in aws_observation["observed_controls"]
                    for source in control["aws_evidence_sources"]
                }
            )
            missing_sources = sorted(set(expected_sources) - set(aws_sources))
            source_counts.update(aws_sources)
            missing_source_counts.update(missing_sources)

        aws_status = generic["postcondition_status"]
        findings = list(generic["findings"])
        if generic["coverage"] == "observed" and missing_sources:
            aws_status = "gap"
            findings.append(f"Missing expected AWS evidence source: {', '.join(missing_sources)}.")
        status_counts[aws_status] += 1
        records.append(
            {
                **generic,
                "aws_surface": surface,
                "expected_aws_evidence_sources": expected_sources,
                "observed_aws_evidence_sources": aws_sources,
                "missing_aws_evidence_sources": missing_sources,
                "aws_postcondition_status": aws_status,
                "findings": findings,
            }
        )

    observed = sum(1 for item in records if item["coverage"] == "observed")
    official_sources = [
        "Amazon Bedrock AgentCore Gateway CloudTrail management events",
        "Amazon Bedrock AgentCore Gateway CloudTrail data events for InvokeGateway when explicitly enabled",
        "Amazon Bedrock AgentCore Runtime and Gateway CloudWatch logs, metrics, and spans",
        "AgentCore runtime usage logs with one-second CPU and memory usage fields",
        "AgentCore tool result metadata stream entries",
        "AgentCore Gateway MCP logging notifications",
        "native AWS change records such as IAM, CloudFormation, S3, Secrets Manager, and cost anomaly summaries",
    ]
    return {
        "version": VERSION,
        "generated_at": _now(),
        "source_evaluation_version": generic_report["source_evaluation_version"],
        "source_organization": generic_report["source_organization"],
        "evaluated_actions": generic_report["evaluated_actions"],
        "observed_actions": observed,
        "aws_evidence_source_counts": dict(sorted(source_counts.items())),
        "missing_aws_evidence_source_counts": dict(sorted(missing_source_counts.items())),
        "aws_postcondition_status_counts": dict(sorted(status_counts.items())),
        "records": records,
        "aws_official_signal_surfaces_used_as_model": official_sources,
        "evidence_boundary": (
            "This is metadata-only AWS-style postcondition evidence. It does not call AWS APIs, read live AWS accounts, "
            "collect raw CloudTrail, collect raw CloudWatch logs, expose account IDs, expose ARNs, or prove AWS production "
            "enforcement. It shows what safe observation fields a customer or AWS-style reviewer could export to prove "
            "that SMERC-required controls happened after routing."
        ),
        "work_result_impact": {
            "work": (
                "Compare SMERC/SPARTa route controls for AWS-style actions against safe postcondition observations "
                "modeled on CloudTrail, CloudWatch, AgentCore Gateway, AgentCore Runtime, MCP gateway logs, and native "
                "AWS change records."
            ),
            "result": (
                f"Assessed {generic_report['evaluated_actions']} AWS-style routed actions, observed {observed}, "
                f"and found AWS postcondition statuses {dict(sorted(status_counts.items()))}."
            ),
            "impact": (
                "SMERC can now show how an AWS-style governed action bot would prove that controls were actually "
                "applied after a decision, not only that recoverability scoring recommended them."
            ),
        },
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# AWS Postcondition Evidence Report",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Version: `{report['version']}`",
        "",
        "## Purpose",
        "",
        "This report shows how AWS-style observation metadata could prove whether SMERC-required controls actually happened after a route decision.",
        "",
        "## Work / Result / Impact",
        "",
        f"- Work: {report['work_result_impact']['work']}",
        f"- Result: {report['work_result_impact']['result']}",
        f"- Impact: {report['work_result_impact']['impact']}",
        "",
        "## AWS Signal Surfaces Modeled",
        "",
    ]
    for item in report["aws_official_signal_surfaces_used_as_model"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Evidence Boundary",
            "",
            str(report["evidence_boundary"]),
            "",
            "## Summary",
            "",
            f"- Evaluated actions: `{report['evaluated_actions']}`",
            f"- Observed actions: `{report['observed_actions']}`",
            f"- AWS postcondition status counts: `{report['aws_postcondition_status_counts']}`",
            f"- Observed AWS evidence sources: `{report['aws_evidence_source_counts']}`",
            f"- Missing AWS evidence sources: `{report['missing_aws_evidence_source_counts']}`",
            "",
            "## Action Checks",
            "",
            "| Action | AWS surface | Route | Execution | Missing route controls | Missing AWS sources | Status |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in report["records"]:
        lines.append(
            f"| `{item['action_id']}` | `{item['aws_surface']}` | `{item['route_state']}` | "
            f"`{item['execution_status']}` | `{item['missing_controls']}` | "
            f"`{item['missing_aws_evidence_sources']}` | `{item['aws_postcondition_status']}` |"
        )
    lines.extend(
        [
            "",
            "## Reviewer Question",
            "",
            "For one AWS-style workflow, can the platform export safe observation metadata that proves preview, scope limit, checkpoint, rollback plan, gateway enforcement, execution block, replay, cost-velocity, and trace evidence without exposing secrets or raw customer logs?",
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


def _to_generic_observation(item: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "action_id": item["action_id"],
        "observed_controls": [
            {
                "control_id": control["control_id"],
                "outcome": control["outcome"],
                "mechanism": control["mechanism"],
                "evidence_ref": control["evidence_ref"],
                "observed_at": control["observed_at"],
            }
            for control in item["observed_controls"]
        ],
        "execution": dict(item["execution"]),
    }


def _normalize_aws_observation(item: Mapping[str, Any], index: int) -> Dict[str, Any]:
    controls = item.get("observed_controls")
    if not isinstance(controls, list):
        raise TypeError(f"observations[{index}].observed_controls must be a list")
    normalized_controls = []
    seen = set()
    for control_index, control in enumerate(controls):
        if not isinstance(control, dict):
            raise TypeError(f"observations[{index}].observed_controls[{control_index}] must be an object")
        control_id = _text(control.get("control_id"), f"observations[{index}].observed_controls[{control_index}].control_id")
        if control_id in seen:
            raise ValueError(f"duplicate observed control {control_id} for action {item['action_id']}")
        seen.add(control_id)
        outcome = _text(control.get("outcome"), f"{control_id}.outcome")
        if outcome not in CONTROL_OUTCOMES:
            raise ValueError(f"{control_id}.outcome must be one of {', '.join(sorted(CONTROL_OUTCOMES))}")
        sources = _sources(control.get("aws_evidence_sources"), f"{control_id}.aws_evidence_sources")
        normalized_controls.append(
            {
                "control_id": control_id,
                "outcome": outcome,
                "mechanism": _text(control.get("mechanism"), f"{control_id}.mechanism", 160),
                "evidence_ref": _text(control.get("evidence_ref"), f"{control_id}.evidence_ref", 256),
                "observed_at": _text(control.get("observed_at"), f"{control_id}.observed_at", 64),
                "aws_evidence_sources": sources,
            }
        )

    execution = item.get("execution")
    if not isinstance(execution, dict):
        raise TypeError(f"observations[{index}].execution must be an object")
    status = _text(execution.get("status"), f"observations[{index}].execution.status")
    if status not in EXECUTION_STATUSES:
        raise ValueError(f"execution.status must be one of {', '.join(sorted(EXECUTION_STATUSES))}")
    rollback_success = execution.get("rollback_success")
    if rollback_success is not None and not isinstance(rollback_success, bool):
        raise TypeError("execution.rollback_success must be boolean or null")

    return {
        "action_id": _text(item.get("action_id"), f"observations[{index}].action_id"),
        "aws_surface": _text(item.get("aws_surface"), f"observations[{index}].aws_surface", 96),
        "expected_aws_evidence_sources": _sources(
            item.get("expected_aws_evidence_sources"),
            f"observations[{index}].expected_aws_evidence_sources",
        ),
        "observed_controls": sorted(normalized_controls, key=lambda value: value["control_id"]),
        "execution": {
            "attempted": _boolean(execution.get("attempted"), "execution.attempted"),
            "status": status,
            "rollback_performed": _boolean(execution.get("rollback_performed"), "execution.rollback_performed"),
            "rollback_success": rollback_success,
            "notes": _text(execution.get("notes"), "execution.notes", 420),
        },
    }


def _sources(values: Any, path: str) -> list[str]:
    if not isinstance(values, list) or not values:
        raise TypeError(f"{path} must be a non-empty list")
    normalized = []
    for item in values:
        if not isinstance(item, str) or not item.strip():
            raise TypeError(f"{path} must contain non-empty strings")
        source = item.strip()
        if source not in AWS_EVIDENCE_SOURCES:
            raise ValueError(f"{path} includes unsupported AWS evidence source: {source}")
        normalized.append(source)
    return sorted(set(normalized))


def _reject_prohibited_fields(value: Any, path: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in PROHIBITED_FIELDS:
                raise ValueError(f"{path}.{key} is prohibited in metadata-only AWS postcondition observations")
            _reject_prohibited_fields(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_prohibited_fields(child, f"{path}[{index}]")


def _text(value: Any, path: str, maximum: int = 128) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    clean = value.strip()
    if len(clean) > maximum:
        raise ValueError(f"{path} must be at most {maximum} characters")
    return clean


def _boolean(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{path} must be a boolean")
    return value


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare AWS-style postcondition evidence with SMERC/SPARTa route controls.")
    parser.add_argument(
        "--evaluation",
        default="reports/aws_metadata_adapter/customer_evaluation_report.json",
        type=Path,
        help="Path to a SMERC AWS customer-evaluation JSON report.",
    )
    parser.add_argument(
        "--observations",
        default="examples/aws_postcondition_observations.json",
        type=Path,
        help="Path to AWS postcondition observation JSON.",
    )
    parser.add_argument("--json-output", default="reports/aws_postcondition_evidence/aws_postcondition_evidence_report.json")
    parser.add_argument("--markdown-output", default="reports/aws_postcondition_evidence/AWS_Postcondition_Evidence_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_aws_postcondition_report(load_json_object(args.evaluation), load_aws_observations(args.observations))
    write_outputs(report, json_path=args.json_output, markdown_path=args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
