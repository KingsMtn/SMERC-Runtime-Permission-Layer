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


VERSION = "smerc.aws-shadow-mirror-adapter.v1"

SUPPORTED_SOURCE_FORMATS = {
    "vpc_traffic_mirror_eni_summary",
    "nlb_udp_fanout_summary",
    "gateway_load_balancer_endpoint_summary",
}

PROHIBITED_FIELDS = {
    "account_id",
    "access_key",
    "arn",
    "aws_secret_access_key",
    "credential",
    "credentials",
    "customer_record",
    "full_packet_capture",
    "packet_payload",
    "payload",
    "private_topology",
    "production_command",
    "raw_flow_log",
    "raw_log",
    "raw_packet",
    "raw_payload",
    "secret",
    "session_token",
}

REQUIRED_TEXT_FIELDS = [
    "record_id",
    "source_format",
    "source_url",
    "mirror_method",
    "capture_window",
    "workflow_family",
    "environment",
    "actor",
    "tool",
    "observed_flow",
    "source_service_class",
    "destination_class",
    "requested_capability",
    "current_control",
]

REQUIRED_RATIO_FIELDS = [
    "traffic_velocity_ratio",
    "anomaly_pressure",
    "reversibility",
    "containment_strength",
    "rollback_latency",
    "evidence_quality",
    "impact_scope",
    "cancel_reliability",
    "authorization_confidence",
    "data_sensitivity_pressure",
]

REQUIRED_BOOL_FIELDS = [
    "payload_inspected",
    "payload_retained",
    "sensitive_pattern_indicator",
    "rollback_path_available",
    "typed_contract",
    "attestation",
    "object_shape",
    "supports_dry_run",
    "supports_scope_limit",
    "supports_checkpoint",
    "supports_rollback",
    "supports_human_approval",
    "postcondition_evidence_expected",
]


def load_source_exports(path: str | Path) -> list[Dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError("AWS shadow mirror adapter input must be a non-empty JSON array")
    rows: list[Dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise TypeError(f"AWS shadow mirror row {index} must be an object")
        record_id = _text(item.get("record_id"), f"rows[{index}].record_id")
        if record_id in seen:
            raise ValueError(f"duplicate record_id: {record_id}")
        seen.add(record_id)
        rows.append(dict(item))
    return rows


def normalize_source_exports(rows: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    accepted: list[Dict[str, Any]] = []
    skipped: list[Dict[str, str]] = []
    for index, row in enumerate(rows, start=1):
        record_id = str(row.get("record_id", f"row_{index}"))
        skip_reason = _skip_reason(row)
        if skip_reason:
            skipped.append({"record_id": record_id, "reason": skip_reason})
            continue
        accepted.append(_to_customer_action(row, len(accepted) + 1))

    return {
        "version": CUSTOMER_EVALUATION_VERSION,
        "tenant_id": "aws-shadow-mirror-review",
        "organization": "AWS Shadow Mirror Review",
        "contact_role": "cloud_security_or_platform_reviewer",
        "evaluation_date": datetime.now(timezone.utc).date().isoformat(),
        "data_boundary": (
            "AWS shadow mirror evaluation. Inputs are derived flow summaries only. No packet payloads, retained "
            "payload content, AWS credentials, account IDs, ARNs, raw logs, private topology, customer records, "
            "secrets, production commands, or live AWS access are included."
        ),
        "workflow_context": (
            "Non-executing AWS-style shadow mirror adapter normalizing sanitized VPC Traffic Mirroring, Network "
            "Load Balancer fan-out, or Gateway Load Balancer endpoint summaries into SMERC customer-evaluation "
            "actions for shadow-mode review."
        ),
        "initial_autonomy_state": "HEALTHY",
        "actions": accepted,
        "adapter_summary": {
            "accepted_rows": len(accepted),
            "skipped_rows": len(skipped),
            "skipped": skipped,
            "source_version": VERSION,
        },
    }


def build_adapter_report(rows: list[Mapping[str, Any]]) -> Dict[str, Any]:
    payload = normalize_source_exports(rows)
    customer_payload = _customer_payload(payload)
    evaluation = build_customer_evaluation(customer_payload) if customer_payload["actions"] else None
    actions = payload["actions"]
    skipped_reasons = Counter(item["reason"] for item in payload["adapter_summary"]["skipped"])
    return {
        "version": VERSION,
        "generated_at": _now(),
        "source_export_count": len(rows),
        "accepted_rows": payload["adapter_summary"]["accepted_rows"],
        "skipped_rows": payload["adapter_summary"]["skipped_rows"],
        "skipped": payload["adapter_summary"]["skipped"],
        "mirror_method_counts": _counter_from_metadata(actions, "mirror_method"),
        "destination_class_counts": _counter_from_metadata(actions, "destination_class"),
        "high_velocity_flow_count": sum(
            1 for action in actions if action["tool_plan"]["metadata"]["traffic_velocity_ratio"] >= 0.75
        ),
        "sensitive_pattern_flow_count": sum(
            1 for action in actions if action["tool_plan"]["metadata"]["sensitive_pattern_indicator"] is True
        ),
        "skipped_reason_counts": dict(sorted(skipped_reasons.items())),
        "normalized_customer_evaluation": customer_payload,
        "customer_evaluation": evaluation,
        "evidence_boundary": (
            "The adapter is a non-executing shadow-mode proof. It does not configure VPC Traffic Mirroring, attach "
            "ENIs, create NLB or Gateway Load Balancer targets, inspect packet payloads, retain payload content, "
            "call AWS APIs, assume roles, read live accounts, or enforce network policy."
        ),
        "work_result_impact": {
            "work": (
                "Accept sanitized AWS mirror-derived flow summaries and reject unsafe rows before recoverability "
                "scoring."
            ),
            "result": (
                f"Accepted {payload['adapter_summary']['accepted_rows']} mirror summaries, skipped "
                f"{payload['adapter_summary']['skipped_rows']} unsafe or unsupported rows, and normalized accepted "
                "rows into the SMERC customer-evaluation contract."
            ),
            "impact": (
                "An AWS-style infrastructure reviewer can test SMERC against real operational flow metadata in "
                "shadow mode without exposing packet payloads, secrets, account identifiers, or live cloud access."
            ),
        },
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# AWS Shadow Mirror Adapter Report",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Version: `{report['version']}`",
        "",
        "## Purpose",
        "",
        "This report shows how SMERC can use sanitized AWS mirror-derived metadata as a shadow-mode evidence source.",
        "",
        "It is not a firewall path. It is a safe observability path for testing recoverability posture before enforcement.",
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
        "## Adapter Intake",
        "",
        f"- Source export rows: `{report['source_export_count']}`",
        f"- Accepted rows: `{report['accepted_rows']}`",
        f"- Skipped rows: `{report['skipped_rows']}`",
        f"- Mirror methods: `{report['mirror_method_counts']}`",
        f"- Destination classes: `{report['destination_class_counts']}`",
        f"- High velocity accepted flows: `{report['high_velocity_flow_count']}`",
        f"- Sensitive-pattern accepted flows: `{report['sensitive_pattern_flow_count']}`",
        f"- Skipped reason counts: `{report['skipped_reason_counts']}`",
        "",
        "## Skipped Rows",
        "",
        "| Record | Reason |",
        "| --- | --- |",
    ]
    for item in report["skipped"]:
        lines.append(f"| `{item['record_id']}` | {item['reason']} |")

    if report["customer_evaluation"]:
        summary = report["customer_evaluation"]["summary"]
        lines.extend(
            [
                "",
                "## SMERC Evaluation Summary",
                "",
                f"- Posture counts: `{summary['posture_counts']}`",
                f"- Route counts: `{summary['route_state_counts']}`",
                f"- Ref-gate counts: `{summary['ref_gate_counts']}`",
                f"- Valid DLL ledgers: `{summary['valid_ledgers']}`",
                f"- Pilot fit: `{report['customer_evaluation']['pilot_fit']['fit']}`",
                "",
                "## Highest Exposure Accepted Flows",
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
            "Can one AWS workflow export 5 to 25 sanitized mirror-derived summaries without payloads? If yes, SMERC can be evaluated in shadow mode before any enforcement discussion.",
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
    if report["customer_evaluation"]:
        write_customer_outputs(report["customer_evaluation"], customer_json_output, customer_markdown_output)


def _to_customer_action(row: Mapping[str, Any], index: int) -> Dict[str, Any]:
    observed_flow = _text(row.get("observed_flow"), "observed_flow")
    source_format = _text(row.get("source_format"), "source_format")
    action_type = _action_type(row)
    action_id = f"AWS_MIRROR_{index:03d}_{_slug(observed_flow)}"
    return {
        "action_id": action_id,
        "description": (
            f"Sanitized AWS shadow mirror summary for {source_format}: {observed_flow} "
            f"during {row['capture_window']}."
        ),
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
        "external_side_effect": _destination_is_external(row),
        "sensitive_data": _ratio(row.get("data_sensitivity_pressure"), "data_sensitivity_pressure") >= 0.5
        or _boolean(row.get("sensitive_pattern_indicator"), "sensitive_pattern_indicator"),
        "context": {
            "domain_profile": "cloud_admin",
            "source_format": source_format,
            "source_url": _text(row.get("source_url"), "source_url"),
            "workflow": _text(row.get("workflow_family"), "workflow_family"),
            "current_control": _current_control(row),
        },
        "ref_gate": {
            "typed_contract_valid": _boolean(row.get("typed_contract"), "typed_contract"),
            "attestation_valid": _boolean(row.get("attestation"), "attestation"),
            "least_privilege_confirmed": _ratio(row.get("authorization_confidence"), "authorization_confidence") >= 0.6,
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
                "adapter_mode": "shadow_observe_only",
                "cloud_provider": "aws",
                "mirror_method": _text(row.get("mirror_method"), "mirror_method"),
                "capture_window": _text(row.get("capture_window"), "capture_window"),
                "source_format": source_format,
                "source_record_id": _text(row.get("record_id"), "record_id"),
                "source_service_class": _text(row.get("source_service_class"), "source_service_class"),
                "destination_class": _text(row.get("destination_class"), "destination_class"),
                "traffic_velocity_ratio": _ratio(row.get("traffic_velocity_ratio"), "traffic_velocity_ratio"),
                "data_sensitivity_pressure": _ratio(
                    row.get("data_sensitivity_pressure"),
                    "data_sensitivity_pressure",
                ),
                "sensitive_pattern_indicator": _boolean(
                    row.get("sensitive_pattern_indicator"),
                    "sensitive_pattern_indicator",
                ),
                "payload_boundary": {
                    "payload_inspected": False,
                    "payload_retained": False,
                    "derived_metadata_only": True,
                },
                "rollback_path_available": _boolean(row.get("rollback_path_available"), "rollback_path_available"),
                "postcondition_evidence_expected": _boolean(
                    row.get("postcondition_evidence_expected"),
                    "postcondition_evidence_expected",
                ),
            },
        },
    }


def _customer_payload(payload: Mapping[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in payload.items() if key != "adapter_summary"}


def _skip_reason(row: Mapping[str, Any]) -> str | None:
    for key in row:
        normalized = str(key).strip().lower()
        if normalized in PROHIBITED_FIELDS:
            return f"prohibited field present: {normalized}"
    source_format = row.get("source_format")
    if not isinstance(source_format, str) or source_format not in SUPPORTED_SOURCE_FORMATS:
        return "unsupported source_format"
    try:
        _required_shape(row)
    except (TypeError, ValueError) as exc:
        return f"invalid required field: {exc}"
    if _boolean(row.get("payload_inspected"), "payload_inspected"):
        return "payload inspection is outside the public SMERC shadow mirror boundary"
    if _boolean(row.get("payload_retained"), "payload_retained"):
        return "payload retention is outside the public SMERC shadow mirror boundary"
    return None


def _required_shape(row: Mapping[str, Any]) -> None:
    for key in REQUIRED_TEXT_FIELDS:
        _text(row.get(key), key)
    for key in REQUIRED_RATIO_FIELDS:
        _ratio(row.get(key), key)
    for key in REQUIRED_BOOL_FIELDS:
        _boolean(row.get(key), key)
    _positive_number(row.get("max_scope_units"), "max_scope_units")
    _positive_number(row.get("requested_scope_units"), "requested_scope_units")
    _current_control(row)


def _action_type(row: Mapping[str, Any]) -> str:
    source_format = _text(row.get("source_format"), "source_format")
    if source_format == "vpc_traffic_mirror_eni_summary":
        return "aws_vpc_mirror_flow_review"
    if source_format == "nlb_udp_fanout_summary":
        return "aws_nlb_mirror_fanout_review"
    if source_format == "gateway_load_balancer_endpoint_summary":
        return "aws_gwlb_endpoint_flow_review"
    return _slug(_text(row.get("observed_flow"), "observed_flow"))


def _risk(row: Mapping[str, Any], action_type: str) -> float:
    velocity = _ratio(row.get("traffic_velocity_ratio"), "traffic_velocity_ratio")
    anomaly = _ratio(row.get("anomaly_pressure"), "anomaly_pressure")
    sensitivity = _ratio(row.get("data_sensitivity_pressure"), "data_sensitivity_pressure")
    impact = _ratio(row.get("impact_scope"), "impact_scope")
    reversibility_gap = 1.0 - _ratio(row.get("reversibility"), "reversibility")
    evidence_gap = 1.0 - _ratio(row.get("evidence_quality"), "evidence_quality")
    risk = (
        velocity * 0.2
        + anomaly * 0.22
        + sensitivity * 0.18
        + impact * 0.18
        + reversibility_gap * 0.14
        + evidence_gap * 0.08
    )
    if _boolean(row.get("sensitive_pattern_indicator"), "sensitive_pattern_indicator"):
        risk += 0.1
    if _destination_is_external(row):
        risk += 0.06
    if not _boolean(row.get("rollback_path_available"), "rollback_path_available"):
        risk += 0.05
    if action_type == "aws_gwlb_endpoint_flow_review":
        risk += 0.02
    return round(min(1.0, risk), 3)


def _side_effect(row: Mapping[str, Any]) -> str:
    destination = _text(row.get("destination_class"), "destination_class")
    if "internet" in destination or "external" in destination:
        return "external"
    if _ratio(row.get("data_sensitivity_pressure"), "data_sensitivity_pressure") >= 0.75:
        return "external"
    return "internal"


def _destination_is_external(row: Mapping[str, Any]) -> bool:
    destination = _text(row.get("destination_class"), "destination_class").lower()
    return "internet" in destination or "external" in destination or "third_party" in destination


def _counter_from_metadata(actions: Iterable[Mapping[str, Any]], key: str) -> Dict[str, int]:
    counts: Counter[str] = Counter()
    for action in actions:
        value = action["tool_plan"]["metadata"].get(key)
        if value:
            counts[str(value)] += 1
    return dict(sorted(counts.items()))


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
    parser = argparse.ArgumentParser(
        description="Normalize sanitized AWS shadow mirror summaries into SMERC evaluation actions."
    )
    parser.add_argument("path", help="Path to AWS shadow mirror source export JSON.")
    parser.add_argument(
        "--normalized-output",
        default="examples/aws_shadow_mirror_normalized_customer_eval_actions.json",
    )
    parser.add_argument(
        "--json-output",
        default="reports/aws_shadow_mirror/aws_shadow_mirror_adapter_report.json",
    )
    parser.add_argument(
        "--markdown-output",
        default="reports/aws_shadow_mirror/AWS_Shadow_Mirror_Adapter_Report.md",
    )
    parser.add_argument(
        "--customer-json-output",
        default="reports/aws_shadow_mirror/customer_evaluation_report.json",
    )
    parser.add_argument(
        "--customer-markdown-output",
        default="reports/aws_shadow_mirror/Customer_Evaluation_Report.md",
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_adapter_report(load_source_exports(args.path))
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
