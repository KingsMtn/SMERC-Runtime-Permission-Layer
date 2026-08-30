from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from reference_engine.customer_evaluation import (
    CUSTOMER_EVALUATION_VERSION,
    build_customer_evaluation,
    write_outputs as write_customer_outputs,
)


VERSION = "smerc.cloud-metadata-connector.v1"

SUPPORTED_SOURCE_FORMATS = {
    "backup_policy_change",
    "cloudtrail_event_summary",
    "dns_change_request",
    "iam_access_analyzer_finding",
    "kubernetes_rollout_plan",
    "terraform_plan_change",
}


def load_source_exports(path: str | Path) -> list[Dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError("cloud source export input must be a non-empty JSON array")
    rows: list[Dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise TypeError(f"cloud source export row {index} must be an object")
        record_id = _text(item.get("record_id"), f"source export row {index} record_id")
        if record_id in seen:
            raise ValueError(f"duplicate record_id: {record_id}")
        seen.add(record_id)
        source_format = _text(item.get("source_format"), f"{record_id} source_format")
        if source_format not in SUPPORTED_SOURCE_FORMATS:
            raise ValueError(f"{record_id} source_format must be one of {', '.join(sorted(SUPPORTED_SOURCE_FORMATS))}")
        rows.append(dict(item))
    return rows


def normalize_source_exports(rows: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    actions = []
    for index, row in enumerate(rows, start=1):
        actions.append(_to_customer_action(row, index))
    return {
        "version": CUSTOMER_EVALUATION_VERSION,
        "tenant_id": "cloud-metadata-review",
        "organization": "Cloud Metadata Review",
        "contact_role": "cloud_platform_reviewer",
        "evaluation_date": datetime.now(timezone.utc).date().isoformat(),
        "data_boundary": (
            "Cloud metadata connector evaluation. Inputs are exported summaries only. No cloud credentials, account "
            "identifiers, private network details, raw logs, source code, secrets, customer records, or live "
            "infrastructure commands are included."
        ),
        "workflow_context": (
            "Read-only cloud change metadata normalized into SMERC customer-evaluation actions for IAM, network, "
            "database, Kubernetes, DNS, and backup-policy review."
        ),
        "initial_autonomy_state": "HEALTHY",
        "actions": actions,
    }


def build_connector_report(rows: list[Mapping[str, Any]]) -> Dict[str, Any]:
    payload = normalize_source_exports(rows)
    evaluation = build_customer_evaluation(payload)
    source_counts = Counter(str(row["source_format"]) for row in rows)
    current_controls = Counter(str(row["current_control"]).upper() for row in rows)
    return {
        "version": VERSION,
        "generated_at": _now(),
        "source_export_count": len(rows),
        "normalized_action_count": len(payload["actions"]),
        "source_format_counts": dict(sorted(source_counts.items())),
        "current_control_counts": dict(sorted(current_controls.items())),
        "normalized_customer_evaluation": payload,
        "customer_evaluation": evaluation,
        "evidence_boundary": (
            "The connector normalizes exported cloud-change summaries into SMERC metadata. It does not call AWS, "
            "Azure, Google Cloud, Cloudflare, Kubernetes, Terraform, DNS providers, databases, secrets managers, "
            "or production systems."
        ),
        "work_result_impact": {
            "work": "Convert safe cloud-change exports into strict SMERC customer-evaluation actions.",
            "result": (
                f"Generated {len(payload['actions'])} normalized actions and evaluated them through Ref-gates, "
                "recoverability scoring, SPARTa routing, autonomy budgeting, and DLL evidence."
            ),
            "impact": (
                "A company can test SMERC against familiar cloud-admin evidence before granting live access or "
                "building an enforcement integration."
            ),
        },
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    summary = report["customer_evaluation"]["summary"]
    lines = [
        "# Cloud Metadata Connector Report",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Version: `{report['version']}`",
        "",
        "## Purpose",
        "",
        "This report shows the practical bridge between a real company's cloud-change evidence and the SMERC runtime evaluation contract.",
        "",
        "Instead of asking for credentials or live infrastructure access, the connector accepts read-only exported summaries and converts them into metadata-only SMERC actions.",
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
        "## Source Export Formats",
        "",
        "| Source export format | Rows |",
        "| --- | ---: |",
    ]
    for source_format, count in report["source_format_counts"].items():
        lines.append(f"| `{source_format}` | {count} |")
    lines.extend(
        [
            "",
            "## Current Controls vs SMERC Result",
            "",
            f"- Current control counts: `{report['current_control_counts']}`",
            f"- SMERC posture counts: `{summary['posture_counts']}`",
            f"- SPARTa route counts: `{summary['route_state_counts']}`",
            f"- Ref-gate counts: `{summary['ref_gate_counts']}`",
            f"- Valid DLL ledgers: `{summary['valid_ledgers']}`",
            f"- Pilot fit: `{report['customer_evaluation']['pilot_fit']['fit']}`",
            "",
            "## Highest Exposure Actions",
            "",
            "| Action | Posture | Route | Exposure |",
            "| --- | --- | --- | ---: |",
        ]
    )
    for item in summary["highest_exposure_actions"]:
        lines.append(
            f"| `{item['action_id']}` | `{item['posture']}` | `{item['route_state']}` | "
            f"{item['irreversible_exposure_score']} |"
        )
    lines.extend(
        [
            "",
            "## Reviewer Question",
            "",
            "Can this exported metadata be produced before the agent or automation executes the action? If yes, SMERC can run in shadow mode without live credentials.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(
    report: Mapping[str, Any],
    *,
    normalized_output: str | Path,
    json_output: str | Path,
    markdown_output: str | Path,
    customer_json_output: str | Path,
    customer_markdown_output: str | Path,
) -> None:
    normalized_path = Path(normalized_output)
    json_path = Path(json_output)
    markdown_path = Path(markdown_output)
    normalized_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    normalized_path.write_text(
        json.dumps(report["normalized_customer_evaluation"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    write_customer_outputs(report["customer_evaluation"], customer_json_output, customer_markdown_output)


def _to_customer_action(row: Mapping[str, Any], index: int) -> Dict[str, Any]:
    source_format = _text(row.get("source_format"), "source_format")
    proposed_action = _text(row.get("proposed_action"), "proposed_action")
    action_type = _action_type(source_format, proposed_action)
    action_id = f"CLOUD_EXPORT_{index:03d}_{_slug(proposed_action)}"
    return {
        "action_id": action_id,
        "description": _description(row, action_type),
        "actor": _text(row.get("actor"), "actor"),
        "tool": _text(row.get("tool"), "tool"),
        "action_type": action_type,
        "base_action_risk": _risk(row, action_type),
        "reversibility": _ratio(row.get("reversibility"), "reversibility"),
        "containment_strength": _ratio(row.get("containment_strength"), "containment_strength"),
        "rollback_latency": _ratio(row.get("rollback_latency"), "rollback_latency"),
        "evidence_validity": _ratio(row.get("evidence_quality"), "evidence_quality"),
        "anomaly_pressure": _ratio(row.get("anomaly_pressure"), "anomaly_pressure"),
        "impact_scope": _ratio(row.get("impact_scope"), "impact_scope"),
        "cancel_reliability": _ratio(row.get("cancel_reliability"), "cancel_reliability"),
        "authorization_confidence": _ratio(row.get("authorization_confidence"), "authorization_confidence"),
        "external_side_effect": True,
        "sensitive_data": _boolean(row.get("sensitive_data"), "sensitive_data"),
        "context": {
            "domain_profile": "cloud_admin",
            "source_format": source_format,
            "source_url": _text(row.get("source_url"), "source_url"),
            "workflow": _text(row.get("change_family"), "change_family"),
            "current_control": _current_control(row),
        },
        "ref_gate": {
            "typed_contract_valid": _boolean(row.get("typed_contract"), "typed_contract"),
            "attestation_valid": _boolean(row.get("attestation"), "attestation"),
            "least_privilege_confirmed": _ratio(row.get("least_privilege"), "least_privilege") >= 0.6,
            "object_shape_expected": _boolean(row.get("object_shape"), "object_shape"),
        },
        "tool_plan": {
            "version": "smerc.sparta-plan.v1",
            "plan_id": f"plan_{action_id.lower()}",
            "tool": _text(row.get("tool"), "tool"),
            "action": action_type,
            "requested_capability": _text(row.get("requested_capability"), "requested_capability"),
            "supports_dry_run": _boolean(row.get("supports_dry_run"), "supports_dry_run"),
            "supports_scope_limit": _boolean(row.get("supports_scope_limit"), "supports_scope_limit"),
            "supports_checkpoint": _boolean(row.get("supports_checkpoint"), "supports_checkpoint"),
            "supports_rollback": _boolean(row.get("supports_rollback"), "supports_rollback"),
            "supports_human_approval": _boolean(row.get("supports_human_approval"), "supports_human_approval"),
            "max_scope_units": int(_positive_number(row.get("max_scope_units"), "max_scope_units")),
            "requested_scope_units": int(_positive_number(row.get("requested_scope_units"), "requested_scope_units")),
            "side_effect_level": _side_effect(row),
            "metadata": {
                "environment": _text(row.get("environment"), "environment"),
                "change_family": _text(row.get("change_family"), "change_family"),
                "source_format": source_format,
                "source_record_id": _text(row.get("record_id"), "record_id"),
            },
        },
    }


def _action_type(source_format: str, proposed_action: str) -> str:
    mapping = {
        "backup_policy_change": "backup_retention_reduction",
        "cloudtrail_event_summary": "database_cluster_delete",
        "dns_change_request": "production_dns_cutover",
        "iam_access_analyzer_finding": "iam_policy_expansion",
        "kubernetes_rollout_plan": "production_canary_rollout",
        "terraform_plan_change": "security_group_change",
    }
    return mapping.get(source_format, _slug(proposed_action))


def _description(row: Mapping[str, Any], action_type: str) -> str:
    return (
        f"Read-only {row['source_format']} export proposes {action_type} in {row['environment']} "
        f"for {row['change_family']}."
    )


def _risk(row: Mapping[str, Any], action_type: str) -> float:
    impact = _ratio(row.get("impact_scope"), "impact_scope")
    reversibility_gap = 1.0 - _ratio(row.get("reversibility"), "reversibility")
    anomaly = _ratio(row.get("anomaly_pressure"), "anomaly_pressure")
    risk = impact * 0.42 + reversibility_gap * 0.36 + anomaly * 0.22
    if "delete" in action_type or _side_effect(row) == "destructive":
        risk += 0.12
    return round(min(1.0, risk), 3)


def _side_effect(row: Mapping[str, Any]) -> str:
    value = _text(row.get("side_effect_level"), "side_effect_level")
    if value not in {"internal", "external", "destructive", "financial"}:
        raise ValueError("side_effect_level must be internal, external, destructive, or financial")
    return value


def _current_control(row: Mapping[str, Any]) -> str:
    value = _text(row.get("current_control"), "current_control").upper()
    if value not in {"ALLOW", "REVIEW", "ALERT", "BLOCK"}:
        raise ValueError("current_control must be ALLOW, REVIEW, ALERT, or BLOCK")
    return value


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    return value.strip()


def _boolean(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{path} must be a boolean")
    return value


def _ratio(value: Any, path: str) -> float:
    numeric = _positive_number(value, path)
    if numeric > 1.0:
        raise ValueError(f"{path} must be between 0.0 and 1.0")
    return round(numeric, 3)


def _positive_number(value: Any, path: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise TypeError(f"{path} must be a number")
    numeric = float(value)
    if numeric < 0:
        raise ValueError(f"{path} must be non-negative")
    return numeric


def _slug(value: str) -> str:
    clean = [char.lower() if char.isalnum() else "_" for char in value]
    return "_".join(part for part in "".join(clean).split("_") if part)[:72]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize read-only cloud metadata exports into SMERC evaluation actions.")
    parser.add_argument("path", help="Path to cloud metadata source export JSON.")
    parser.add_argument("--normalized-output", default="examples/cloud_admin_normalized_customer_eval_actions.json")
    parser.add_argument("--json-output", default="reports/cloud_metadata_connector_report.json")
    parser.add_argument("--markdown-output", default="reports/Cloud_Metadata_Connector_Report.md")
    parser.add_argument("--customer-json-output", default="reports/cloud_metadata_customer_evaluation/customer_evaluation_report.json")
    parser.add_argument("--customer-markdown-output", default="reports/cloud_metadata_customer_evaluation/Customer_Evaluation_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_connector_report(load_source_exports(args.path))
    write_outputs(
        report,
        normalized_output=args.normalized_output,
        json_output=args.json_output,
        markdown_output=args.markdown_output,
        customer_json_output=args.customer_json_output,
        customer_markdown_output=args.customer_markdown_output,
    )
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
