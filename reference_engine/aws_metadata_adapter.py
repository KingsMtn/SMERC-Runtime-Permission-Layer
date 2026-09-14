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


VERSION = "smerc.aws-metadata-adapter.v1"

SUPPORTED_SOURCE_FORMATS = {
    "agentcore_gateway_tool_call_summary",
    "agentcore_runtime_invocation_summary",
    "cloudformation_changeset_summary",
    "cloudwatch_remediation_summary",
    "config_drift_remediation_summary",
    "cost_anomaly_action_summary",
    "cross_account_delegation_summary",
    "iam_policy_change_summary",
    "rds_operation_summary",
    "s3_policy_change_summary",
    "secrets_rotation_summary",
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

SESSION_CONTEXT_FIELDS = [
    "gateway_only_path",
    "gateway_bypass_detected",
    "delegated_on_behalf_of",
    "principal_type",
    "session_mode",
    "server_initiated_elicitation",
    "server_initiated_sampling",
    "tool_discovery_method",
    "approval_mode",
    "temporal_policy_context",
    "progress_notification_observed",
    "message_notification_observed",
]

POLICY_CONTEXT_FIELDS = [
    "gateway_target_type",
    "target_registered",
    "policy_language",
    "policy_engine_decision",
    "policy_schema_validated",
    "policy_analysis_result",
    "inline_tool_permissions_present",
    "parameter_constraints_present",
]

DERIVED_OUTPUT_FIELDS = [
    "input_sensitivity_level",
    "output_sensitivity_level",
    "access_control_composition",
    "regulatory_tags",
    "derived_output_contains_restricted_summary",
]

AGENTCORE_RUNTIME_FIELDS = [
    "session_user_binding",
    "credential_exposure_class",
    "command_execution_class",
    "audit_correlation_available",
]


def load_source_exports(path: str | Path) -> list[Dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError("AWS metadata adapter input must be a non-empty JSON array")
    rows: list[Dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise TypeError(f"AWS metadata row {index} must be an object")
        record_id = _text(item.get("record_id"), f"AWS metadata row {index} record_id")
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
        "tenant_id": "aws-metadata-adapter-review",
        "organization": "AWS Metadata Adapter Review",
        "contact_role": "aws_platform_security_reviewer",
        "evaluation_date": datetime.now(timezone.utc).date().isoformat(),
        "data_boundary": (
            "AWS metadata adapter evaluation. Inputs are exported summaries only. No AWS credentials, account IDs, "
            "ARNs, raw logs, private topology, customer records, secrets, production commands, or live AWS access "
            "are included."
        ),
        "workflow_context": (
            "Non-executing AWS-style metadata adapter normalizing safe summaries into SMERC customer-evaluation "
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
    accepted_source_counts = Counter(
        action["context"]["source_format"] for action in payload["actions"]
    )
    session_summary = _session_summary(payload["actions"])
    skipped_reasons = Counter(item["reason"] for item in payload["adapter_summary"]["skipped"])
    return {
        "version": VERSION,
        "generated_at": _now(),
        "source_export_count": len(rows),
        "accepted_rows": payload["adapter_summary"]["accepted_rows"],
        "skipped_rows": payload["adapter_summary"]["skipped_rows"],
        "skipped": payload["adapter_summary"]["skipped"],
        "accepted_source_format_counts": dict(sorted(accepted_source_counts.items())),
        "session_and_delegated_approval_summary": session_summary,
        "agentcore_runtime_security_summary": _agentcore_runtime_summary(payload["actions"]),
        "policy_engine_summary": _policy_summary(payload["actions"]),
        "derived_output_governance_summary": _derived_output_summary(payload["actions"]),
        "skipped_reason_counts": dict(sorted(skipped_reasons.items())),
        "normalized_customer_evaluation": customer_payload,
        "customer_evaluation": evaluation,
        "evidence_boundary": (
            "The adapter is a non-executing stub. It does not call AWS APIs, assume roles, inspect live accounts, "
            "read CloudTrail, execute CloudFormation, modify IAM, access S3, change RDS, trigger remediation, rotate "
            "secrets, or change cross-account trust."
        ),
        "work_result_impact": {
            "work": "Accept safe AWS-style exported summaries and reject unsafe or unsupported rows before scoring.",
            "result": (
                f"Accepted {payload['adapter_summary']['accepted_rows']} rows, skipped "
                f"{payload['adapter_summary']['skipped_rows']} rows, and normalized accepted rows into the "
                "SMERC customer-evaluation contract."
            ),
            "impact": (
                "An AWS-style platform reviewer can test recoverability judgment without granting credentials, "
                "sharing sensitive identifiers, or allowing production execution."
            ),
        },
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# AWS Metadata Adapter Report",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Version: `{report['version']}`",
        "",
        "## Purpose",
        "",
        "This report shows how an AWS-style platform team could export safe action summaries and run them through SMERC without live AWS access.",
        "",
        "The adapter is intentionally non-executing. It accepts metadata summaries, skips unsafe rows, normalizes accepted rows, and then runs SMERC customer evaluation.",
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
        f"- Accepted source formats: `{report['accepted_source_format_counts']}`",
        f"- Session and delegated approval summary: `{report['session_and_delegated_approval_summary']}`",
        f"- AgentCore runtime security summary: `{report['agentcore_runtime_security_summary']}`",
        f"- Policy engine summary: `{report['policy_engine_summary']}`",
        f"- Derived output governance summary: `{report['derived_output_governance_summary']}`",
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
                "## Highest Exposure Accepted Actions",
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
            "Can your AWS-style workflow produce these safe summaries before execution? If yes, SMERC can be tested in shadow mode without credentials.",
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
    source_format = _text(row.get("source_format"), "source_format")
    proposed_action = _text(row.get("proposed_action"), "proposed_action")
    aws_surface = _text(row.get("aws_surface"), "aws_surface")
    action_type = _action_type(source_format, proposed_action)
    action_id = f"AWS_ADAPTER_{index:03d}_{_slug(proposed_action)}"
    return {
        "action_id": action_id,
        "description": (
            f"Non-executing AWS metadata adapter summary for {source_format}: "
            f"{proposed_action} in {row['environment']}."
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
        "external_side_effect": True,
        "sensitive_data": _boolean(row.get("sensitive_data"), "sensitive_data"),
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
                "adapter_mode": "non_executing",
                "cloud_provider": "aws",
                "aws_surface": aws_surface,
                "environment": _text(row.get("environment"), "environment"),
                "workflow_family": _text(row.get("workflow_family"), "workflow_family"),
                "source_format": source_format,
                "source_record_id": _text(row.get("record_id"), "record_id"),
                "gateway_path": _optional_text(row.get("gateway_path")),
                "session_and_delegated_approval_context": _session_context(row),
                "agentcore_runtime_security_context": _agentcore_runtime_context(row),
                "agentcore_policy_context": _policy_context(row),
                "derived_output_governance": _derived_output_context(row),
                "cost_velocity_multiplier": _optional_ratio(row.get("cost_velocity_multiplier")),
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
    return None


def _required_shape(row: Mapping[str, Any]) -> None:
    required_text = [
        "record_id",
        "source_format",
        "source_url",
        "workflow_family",
        "environment",
        "actor",
        "tool",
        "proposed_action",
        "aws_surface",
        "requested_capability",
        "current_control",
    ]
    required_bool = [
        "attestation",
        "object_shape",
        "postcondition_evidence_expected",
        "sensitive_data",
        "supports_checkpoint",
        "supports_dry_run",
        "supports_human_approval",
        "supports_rollback",
        "supports_scope_limit",
        "typed_contract",
    ]
    required_ratio = [
        "anomaly_pressure",
        "authorization_confidence",
        "cancel_reliability",
        "containment_strength",
        "evidence_quality",
        "impact_scope",
        "least_privilege",
        "reversibility",
        "rollback_latency",
    ]
    for key in required_text:
        _text(row.get(key), key)
    for key in required_bool:
        _boolean(row.get(key), key)
    for key in required_ratio:
        _ratio(row.get(key), key)
    _positive_number(row.get("max_scope_units"), "max_scope_units")
    _positive_number(row.get("requested_scope_units"), "requested_scope_units")
    _side_effect(row)
    _current_control(row)


def _action_type(source_format: str, proposed_action: str) -> str:
    mapping = {
        "agentcore_gateway_tool_call_summary": "agentcore_gateway_tool_call",
        "agentcore_runtime_invocation_summary": "agentcore_runtime_invocation",
        "cloudformation_changeset_summary": "cloudformation_changeset_execute",
        "cloudwatch_remediation_summary": "cloudwatch_automated_remediation",
        "config_drift_remediation_summary": "config_drift_remediation",
        "cost_anomaly_action_summary": "cost_velocity_control_change",
        "cross_account_delegation_summary": "cross_account_delegation_change",
        "iam_policy_change_summary": "iam_policy_change",
        "rds_operation_summary": "rds_operation",
        "s3_policy_change_summary": "s3_policy_change",
        "secrets_rotation_summary": "secrets_rotation_change",
    }
    return mapping.get(source_format, _slug(proposed_action))


def _risk(row: Mapping[str, Any], action_type: str) -> float:
    impact = _ratio(row.get("impact_scope"), "impact_scope")
    reversibility_gap = 1.0 - _ratio(row.get("reversibility"), "reversibility")
    anomaly = _ratio(row.get("anomaly_pressure"), "anomaly_pressure")
    evidence_gap = 1.0 - _ratio(row.get("evidence_quality"), "evidence_quality")
    risk = impact * 0.35 + reversibility_gap * 0.28 + anomaly * 0.22 + evidence_gap * 0.15
    if "delete" in action_type or _side_effect(row) in {"destructive", "financial"}:
        risk += 0.12
    if _optional_boolean(row.get("gateway_bypass_detected")):
        risk += 0.08
    if _optional_text(row.get("approval_mode")) == "never" and _side_effect(row) in {"external", "destructive", "financial"}:
        risk += 0.05
    if _optional_text(row.get("session_user_binding")) in {"client_supplied_unverified", "missing", "shared_principal_unbound"}:
        risk += 0.08
    if _optional_text(row.get("credential_exposure_class")) in {"broad_execution_role", "runtime_metadata_credentials"}:
        risk += 0.08
    if _optional_text(row.get("command_execution_class")) in {"interactive_shell", "arbitrary_command"}:
        risk += 0.08
    if _optional_boolean(row.get("audit_correlation_available")) is False:
        risk += 0.05
    return round(min(1.0, risk), 3)


def _current_control(row: Mapping[str, Any]) -> str:
    value = _text(row.get("current_control"), "current_control").upper()
    if value not in {"ALLOW", "REVIEW", "ALERT", "BLOCK"}:
        raise ValueError("current_control must be ALLOW, REVIEW, ALERT, or BLOCK")
    return value


def _side_effect(row: Mapping[str, Any]) -> str:
    value = _text(row.get("side_effect_level"), "side_effect_level")
    if value not in {"internal", "external", "destructive", "financial"}:
        raise ValueError("side_effect_level must be internal, external, destructive, or financial")
    return value


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    return _text(value, "optional text")


def _optional_ratio(value: Any) -> float | None:
    if value is None:
        return None
    return _ratio(value, "optional ratio")


def _optional_boolean(value: Any) -> bool | None:
    if value is None:
        return None
    return _boolean(value, "optional boolean")


def _optional_text_list(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise TypeError("optional text list must be a list")
    return [_text(item, "optional text list item") for item in value]


def _session_context(row: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "gateway_only_path": _optional_boolean(row.get("gateway_only_path")),
        "gateway_bypass_detected": _optional_boolean(row.get("gateway_bypass_detected")),
        "delegated_on_behalf_of": _optional_boolean(row.get("delegated_on_behalf_of")),
        "principal_type": _optional_text(row.get("principal_type")),
        "session_mode": _optional_text(row.get("session_mode")),
        "server_initiated_elicitation": _optional_boolean(row.get("server_initiated_elicitation")),
        "server_initiated_sampling": _optional_boolean(row.get("server_initiated_sampling")),
        "tool_discovery_method": _optional_text(row.get("tool_discovery_method")),
        "approval_mode": _optional_text(row.get("approval_mode")),
        "temporal_policy_context": _optional_text(row.get("temporal_policy_context")),
        "progress_notification_observed": _optional_boolean(row.get("progress_notification_observed")),
        "message_notification_observed": _optional_boolean(row.get("message_notification_observed")),
    }


def _policy_context(row: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "gateway_target_type": _optional_text(row.get("gateway_target_type")),
        "target_registered": _optional_boolean(row.get("target_registered")),
        "policy_language": _optional_text(row.get("policy_language")),
        "policy_engine_decision": _optional_text(row.get("policy_engine_decision")),
        "policy_schema_validated": _optional_boolean(row.get("policy_schema_validated")),
        "policy_analysis_result": _optional_text(row.get("policy_analysis_result")),
        "inline_tool_permissions_present": _optional_boolean(row.get("inline_tool_permissions_present")),
        "parameter_constraints_present": _optional_boolean(row.get("parameter_constraints_present")),
    }


def _derived_output_context(row: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "input_sensitivity_level": _optional_text(row.get("input_sensitivity_level")),
        "output_sensitivity_level": _optional_text(row.get("output_sensitivity_level")),
        "access_control_composition": _optional_text(row.get("access_control_composition")),
        "regulatory_tags": _optional_text_list(row.get("regulatory_tags")),
        "derived_output_contains_restricted_summary": _optional_boolean(
            row.get("derived_output_contains_restricted_summary")
        ),
    }


def _agentcore_runtime_context(row: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "session_user_binding": _optional_text(row.get("session_user_binding")),
        "execution_authority_exposure_class": _optional_text(row.get("credential_exposure_class")),
        "command_execution_class": _optional_text(row.get("command_execution_class")),
        "audit_correlation_available": _optional_boolean(row.get("audit_correlation_available")),
    }


def _session_summary(actions: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    counters: Counter[str] = Counter()
    principal_types: Counter[str] = Counter()
    session_modes: Counter[str] = Counter()
    approval_modes: Counter[str] = Counter()
    for action in actions:
        context = action["tool_plan"]["metadata"]["session_and_delegated_approval_context"]
        if context["gateway_only_path"] is True:
            counters["gateway_only_path"] += 1
        if context["gateway_bypass_detected"] is True:
            counters["gateway_bypass_detected"] += 1
        if context["delegated_on_behalf_of"] is True:
            counters["delegated_on_behalf_of"] += 1
        if context["server_initiated_elicitation"] is True:
            counters["server_initiated_elicitation"] += 1
        if context["server_initiated_sampling"] is True:
            counters["server_initiated_sampling"] += 1
        if context["progress_notification_observed"] is True:
            counters["progress_notification_observed"] += 1
        if context["message_notification_observed"] is True:
            counters["message_notification_observed"] += 1
        if context["principal_type"]:
            principal_types[context["principal_type"]] += 1
        if context["session_mode"]:
            session_modes[context["session_mode"]] += 1
        if context["approval_mode"]:
            approval_modes[context["approval_mode"]] += 1
    return {
        "boolean_counts": dict(sorted(counters.items())),
        "principal_type_counts": dict(sorted(principal_types.items())),
        "session_mode_counts": dict(sorted(session_modes.items())),
        "approval_mode_counts": dict(sorted(approval_modes.items())),
    }


def _policy_summary(actions: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    counters: Counter[str] = Counter()
    decisions: Counter[str] = Counter()
    languages: Counter[str] = Counter()
    target_types: Counter[str] = Counter()
    analysis_results: Counter[str] = Counter()
    for action in actions:
        context = action["tool_plan"]["metadata"]["agentcore_policy_context"]
        if context["target_registered"] is True:
            counters["target_registered"] += 1
        if context["policy_schema_validated"] is True:
            counters["policy_schema_validated"] += 1
        if context["inline_tool_permissions_present"] is True:
            counters["inline_tool_permissions_present"] += 1
        if context["parameter_constraints_present"] is True:
            counters["parameter_constraints_present"] += 1
        if context["policy_engine_decision"]:
            decisions[context["policy_engine_decision"]] += 1
        if context["policy_language"]:
            languages[context["policy_language"]] += 1
        if context["gateway_target_type"]:
            target_types[context["gateway_target_type"]] += 1
        if context["policy_analysis_result"]:
            analysis_results[context["policy_analysis_result"]] += 1
    return {
        "boolean_counts": dict(sorted(counters.items())),
        "policy_engine_decision_counts": dict(sorted(decisions.items())),
        "policy_language_counts": dict(sorted(languages.items())),
        "gateway_target_type_counts": dict(sorted(target_types.items())),
        "policy_analysis_result_counts": dict(sorted(analysis_results.items())),
    }


def _agentcore_runtime_summary(actions: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    session_binding: Counter[str] = Counter()
    execution_authority_exposure: Counter[str] = Counter()
    command_execution: Counter[str] = Counter()
    booleans: Counter[str] = Counter()
    for action in actions:
        context = action["tool_plan"]["metadata"]["agentcore_runtime_security_context"]
        if context["session_user_binding"]:
            session_binding[context["session_user_binding"]] += 1
        if context["execution_authority_exposure_class"]:
            execution_authority_exposure[context["execution_authority_exposure_class"]] += 1
        if context["command_execution_class"]:
            command_execution[context["command_execution_class"]] += 1
        if context["audit_correlation_available"] is True:
            booleans["audit_correlation_available"] += 1
        if context["audit_correlation_available"] is False:
            booleans["audit_correlation_missing"] += 1
    return {
        "session_user_binding_counts": dict(sorted(session_binding.items())),
        "execution_authority_exposure_class_counts": dict(sorted(execution_authority_exposure.items())),
        "command_execution_class_counts": dict(sorted(command_execution.items())),
        "boolean_counts": dict(sorted(booleans.items())),
    }


def _derived_output_summary(actions: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    counters: Counter[str] = Counter()
    input_sensitivity: Counter[str] = Counter()
    output_sensitivity: Counter[str] = Counter()
    compositions: Counter[str] = Counter()
    regulatory_tags: Counter[str] = Counter()
    for action in actions:
        context = action["tool_plan"]["metadata"]["derived_output_governance"]
        if context["derived_output_contains_restricted_summary"] is True:
            counters["restricted_summary_outputs"] += 1
        if context["input_sensitivity_level"]:
            input_sensitivity[context["input_sensitivity_level"]] += 1
        if context["output_sensitivity_level"]:
            output_sensitivity[context["output_sensitivity_level"]] += 1
        if context["access_control_composition"]:
            compositions[context["access_control_composition"]] += 1
        for tag in context["regulatory_tags"]:
            regulatory_tags[tag] += 1
    return {
        "boolean_counts": dict(sorted(counters.items())),
        "input_sensitivity_counts": dict(sorted(input_sensitivity.items())),
        "output_sensitivity_counts": dict(sorted(output_sensitivity.items())),
        "access_control_composition_counts": dict(sorted(compositions.items())),
        "regulatory_tag_counts": dict(sorted(regulatory_tags.items())),
    }


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
    parser = argparse.ArgumentParser(description="Normalize safe AWS-style metadata summaries into SMERC evaluation actions.")
    parser.add_argument("path", help="Path to AWS metadata source export JSON.")
    parser.add_argument("--normalized-output", default="examples/aws_metadata_adapter_normalized_customer_eval_actions.json")
    parser.add_argument("--json-output", default="reports/aws_metadata_adapter/aws_metadata_adapter_report.json")
    parser.add_argument("--markdown-output", default="reports/aws_metadata_adapter/AWS_Metadata_Adapter_Report.md")
    parser.add_argument("--customer-json-output", default="reports/aws_metadata_adapter/customer_evaluation_report.json")
    parser.add_argument("--customer-markdown-output", default="reports/aws_metadata_adapter/Customer_Evaluation_Report.md")
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
