from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Mapping


VERSION = "smerc.recoverability-metadata-contract.v0"
RECORD_VERSION = "smerc.recoverability-metadata.v0"
POSTURES = {"ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE"}
REQUIRED_FIELDS = {
    "version",
    "action_id",
    "action_type",
    "tool_system",
    "reversible",
    "rollback_latency_seconds",
    "external_side_effect",
    "blast_radius_scope",
    "evidence_available",
    "recommended_posture",
}
OPTIONAL_FIELDS = {"confidence_hint", "notes"}
ISOLATION_FIELDS = {
    "tooling_isolation",
    "host_isolation",
    "network_isolation",
    "sandbox_escape_surface",
    "execution_environment_boundary",
}
TOOLING_ISOLATION_VALUES = {
    "none",
    "restricted_tools",
    "shell",
    "browser",
    "code_execution",
    "privileged_automation",
    "unknown",
}
HOST_ISOLATION_VALUES = {"none", "process", "container", "hardened_container", "vm", "dedicated_account", "unknown"}
NETWORK_ISOLATION_VALUES = {"none", "outbound_only", "scoped_private_network", "internet", "production_network", "unknown"}
SANDBOX_ESCAPE_SURFACE_VALUES = {
    "none_known",
    "docker_socket",
    "privileged_container",
    "host_mount",
    "cloud_metadata_access",
    "production_credentials",
    "unknown",
}
EXECUTION_ENVIRONMENT_BOUNDARY_VALUES = {
    "local",
    "ci_runner",
    "mcp_server",
    "cloud_function",
    "bedrock_action_group",
    "kubernetes_workload",
    "production_host",
    "unknown",
}
PROHIBITED_KEY_FRAGMENTS = {
    "secret",
    "token",
    "password",
    "credential",
    "private_key",
    "api_key",
    "raw_log",
    "customer_record",
    "source_code",
}


def load_records(path: str | Path) -> list[Dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, dict) and "records" in payload:
        records = payload["records"]
    else:
        records = payload
    if not isinstance(records, list) or not records:
        raise ValueError("recoverability metadata input must be a non-empty list or an object with records")
    return records


def validate_record(record: Mapping[str, Any]) -> Dict[str, Any]:
    if not isinstance(record, dict):
        raise TypeError("record must be an object")
    _reject_sensitive_keys(record)
    missing = sorted(REQUIRED_FIELDS - set(record))
    unknown = sorted(set(record) - REQUIRED_FIELDS - OPTIONAL_FIELDS - ISOLATION_FIELDS)
    errors = []
    if missing:
        errors.append(f"missing fields: {', '.join(missing)}")
    if unknown:
        errors.append(f"unknown fields: {', '.join(unknown)}")
    if not errors:
        if record["version"] != RECORD_VERSION:
            errors.append(f"version must be {RECORD_VERSION}")
        for field in ["action_id", "action_type", "tool_system", "blast_radius_scope", "evidence_available"]:
            if not isinstance(record[field], str) or not record[field].strip():
                errors.append(f"{field} must be a non-empty string")
        if not isinstance(record["reversible"], bool):
            errors.append("reversible must be a boolean")
        if not isinstance(record["rollback_latency_seconds"], int) or record["rollback_latency_seconds"] < -1:
            errors.append("rollback_latency_seconds must be an integer >= -1")
        if not isinstance(record["external_side_effect"], bool):
            errors.append("external_side_effect must be a boolean")
        if record["recommended_posture"] not in POSTURES:
            errors.append("recommended_posture must be one of ALLOW, THROTTLE, FREEZE, DENY, ESCALATE")
        if "confidence_hint" in record and (
            not isinstance(record["confidence_hint"], (int, float)) or not 0 <= record["confidence_hint"] <= 1
        ):
            errors.append("confidence_hint must be a number between 0 and 1")
        if "notes" in record and not isinstance(record["notes"], str):
            errors.append("notes must be a string")
        _validate_optional_enum(record, "tooling_isolation", TOOLING_ISOLATION_VALUES, errors)
        _validate_optional_enum(record, "host_isolation", HOST_ISOLATION_VALUES, errors)
        _validate_optional_enum(record, "network_isolation", NETWORK_ISOLATION_VALUES, errors)
        _validate_optional_enum(
            record,
            "execution_environment_boundary",
            EXECUTION_ENVIRONMENT_BOUNDARY_VALUES,
            errors,
        )
        if "sandbox_escape_surface" in record:
            surfaces = record["sandbox_escape_surface"]
            if (
                not isinstance(surfaces, list)
                or not surfaces
                or any(not isinstance(item, str) or item not in SANDBOX_ESCAPE_SURFACE_VALUES for item in surfaces)
            ):
                errors.append(
                    "sandbox_escape_surface must be a non-empty list of known escape-surface labels"
                )
            elif "none_known" in surfaces and len(surfaces) > 1:
                errors.append("sandbox_escape_surface cannot combine none_known with other surfaces")
    return {
        "action_id": str(record.get("action_id", "UNKNOWN")),
        "valid": not errors,
        "errors": errors,
        "posture": record.get("recommended_posture"),
        "risk_hint": _risk_hint(record) if not errors else "invalid",
    }


def build_contract_report(records: list[Mapping[str, Any]]) -> Dict[str, Any]:
    validations = [validate_record(record) for record in records]
    valid_records = [record for record in records if validate_record(record)["valid"]]
    posture_counts = Counter(str(record["recommended_posture"]) for record in valid_records)
    risk_hints = Counter(item["risk_hint"] for item in validations)
    environment_boundary_counts = Counter(
        str(record.get("execution_environment_boundary", "unspecified")) for record in valid_records
    )
    host_isolation_counts = Counter(str(record.get("host_isolation", "unspecified")) for record in valid_records)
    return {
        "version": VERSION,
        "record_count": len(records),
        "valid_record_count": sum(1 for item in validations if item["valid"]),
        "invalid_record_count": sum(1 for item in validations if not item["valid"]),
        "posture_counts": dict(sorted(posture_counts.items())),
        "risk_hint_counts": dict(sorted(risk_hints.items())),
        "environment_boundary_counts": dict(sorted(environment_boundary_counts.items())),
        "host_isolation_counts": dict(sorted(host_isolation_counts.items())),
        "validations": validations,
        "work_result_impact": {
            "work": "Define the smallest recoverability metadata shape for individual tool calls and automation actions.",
            "result": "MCP tools, GitHub Actions, AWS-style actions, and other runtimes can describe rollback, side effects, blast radius, evidence, isolation boundaries, and posture hints before execution.",
            "impact": "If this small contract becomes normal, larger SMERC scoring gets cleaner inputs instead of guessing recoverability from logs after the fact.",
        },
        "evidence_boundary": (
            "Recoverability metadata is a hint contract. It does not authorize execution, replace policy engines, "
            "prove safety, or certify production readiness. SMERC or another runtime still has to validate and decide."
        ),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# Recoverability Metadata Contract Report",
        "",
        f"Version: `{report['version']}`",
        "",
        "## Work / Result / Impact",
        "",
        f"- Work: {report['work_result_impact']['work']}",
        f"- Result: {report['work_result_impact']['result']}",
        f"- Impact: {report['work_result_impact']['impact']}",
        "",
        "## Summary",
        "",
        f"- Records: `{report['record_count']}`",
        f"- Valid records: `{report['valid_record_count']}`",
        f"- Invalid records: `{report['invalid_record_count']}`",
        f"- Posture counts: `{report['posture_counts']}`",
        f"- Risk hint counts: `{report['risk_hint_counts']}`",
        f"- Environment boundary counts: `{report['environment_boundary_counts']}`",
        f"- Host isolation counts: `{report['host_isolation_counts']}`",
        "",
        "## Validation Results",
        "",
        "| Action | Valid | Posture | Risk Hint | Errors |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in report["validations"]:
        errors = "; ".join(item["errors"]) if item["errors"] else ""
        lines.append(
            f"| `{item['action_id']}` | `{item['valid']}` | `{item['posture']}` | `{item['risk_hint']}` | {errors} |"
        )
    lines.extend(["", "## Evidence Boundary", "", str(report["evidence_boundary"]), ""])
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], *, json_output: str | Path, markdown_output: str | Path) -> None:
    Path(json_output).parent.mkdir(parents=True, exist_ok=True)
    Path(markdown_output).parent.mkdir(parents=True, exist_ok=True)
    Path(json_output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(markdown_output).write_text(render_markdown(report), encoding="utf-8")


def _risk_hint(record: Mapping[str, Any]) -> str:
    if any(
        surface in {"docker_socket", "privileged_container", "host_mount", "cloud_metadata_access", "production_credentials"}
        for surface in record.get("sandbox_escape_surface", [])
    ):
        return "sandbox_escape_or_credential_surface"
    if not record.get("reversible") or record.get("rollback_latency_seconds") == -1:
        return "recovery_unknown_or_hard"
    if record.get("external_side_effect") and int(record.get("rollback_latency_seconds", 0)) > 60:
        return "side_effect_with_slow_rollback"
    if record.get("external_side_effect"):
        return "bounded_side_effect"
    return "local_or_read_only"


def _validate_optional_enum(
    record: Mapping[str, Any],
    field: str,
    allowed_values: set[str],
    errors: list[str],
) -> None:
    if field in record and (not isinstance(record[field], str) or record[field] not in allowed_values):
        errors.append(f"{field} must be one of {', '.join(sorted(allowed_values))}")


def _reject_sensitive_keys(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower()
            if any(fragment in normalized for fragment in PROHIBITED_KEY_FRAGMENTS):
                raise ValueError(f"{key} appears to contain prohibited sensitive material")
            _reject_sensitive_keys(child)
    elif isinstance(value, list):
        for child in value:
            _reject_sensitive_keys(child)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate SMERC recoverability metadata hint records.")
    parser.add_argument("path", nargs="?", default="examples/recoverability_metadata_examples.json")
    parser.add_argument("--json-output", default="reports/recoverability_metadata_contract_report.json")
    parser.add_argument("--markdown-output", default="reports/Recoverability_Metadata_Contract_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_contract_report(load_records(args.path))
    write_outputs(report, json_output=args.json_output, markdown_output=args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
