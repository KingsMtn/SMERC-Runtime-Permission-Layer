from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping


VERSION = "smerc.dynamic-schema-gate.v1"
SOURCE_NAME = "SMERC Dynamic Schema Gate"

SAFE_CLASSIFICATIONS = {"VALID"}
UNSAFE_SCHEMA_TERMS = {
    "ignore",
    "bypass",
    "override",
    "exfiltrate",
    "leak",
    "credential",
    "secret",
    "token",
    "password",
    "private_key",
}
UNSAFE_ARGUMENT_TERMS = {
    "rm -rf",
    "drop table",
    "delete all",
    "disable audit",
    "stop logging",
    "exfiltrate",
    "leak",
}


def load_payload(path: str | Path) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("dynamic schema gate input must be a JSON object")
    if payload.get("schema_version") != VERSION:
        raise ValueError(f"schema_version must be {VERSION}")
    registry = payload.get("schema_registry")
    calls = payload.get("tool_calls")
    if not isinstance(registry, list) or not registry:
        raise ValueError("schema_registry must be a non-empty list")
    if not isinstance(calls, list) or not calls:
        raise ValueError("tool_calls must be a non-empty list")
    return payload


def build_report(payload: Mapping[str, Any]) -> Dict[str, Any]:
    registry = _registry_by_key(payload["schema_registry"])
    decisions = [evaluate_tool_call(call, registry) for call in payload["tool_calls"]]
    classifications = Counter(decision["classification"] for decision in decisions)
    postures = Counter(decision["smerc_posture"] for decision in decisions)
    routes = Counter(decision["route_hint"] for decision in decisions)
    return {
        "version": VERSION,
        "generated_at": _now(),
        "source_name": SOURCE_NAME,
        "data_boundary": payload.get(
            "data_boundary",
            "Metadata-only local schema-gate examples; no live MCP server, network call, credentials, or customer data.",
        ),
        "registry_count": len(registry),
        "tool_call_count": len(decisions),
        "classification_counts": dict(sorted(classifications.items())),
        "smerc_posture_counts": dict(sorted(postures.items())),
        "route_hint_counts": dict(sorted(routes.items())),
        "decisions": decisions,
        "work_result_impact": {
            "work": "Evaluate MCP/JSON-RPC-style dynamic tool-call schemas before recoverability scoring or network execution.",
            "result": (
                f"Classified {len(decisions)} metadata-only tool calls against {len(registry)} pinned schema entries "
                "using local structural checks, schema-text checks, and argument safety checks."
            ),
            "impact": (
                "SMERC can show that dynamic schema handling is a localized gateway problem: known-good calls can "
                "continue, while drifted, unknown, poisoned, under-specified, or unsafe calls are denied, frozen, "
                "throttled, or escalated before touching an external tool."
            ),
        },
        "evidence_boundary": (
            "This gate is deterministic and local. It is not a full JSON Schema implementation, not a replacement for "
            "MCP clients, not a live proxy trace, not production certification, and not proof that every prompt "
            "injection or schema attack is caught."
        ),
    }


def evaluate_tool_call(call: Mapping[str, Any], registry: Mapping[str, Mapping[str, Any]]) -> Dict[str, Any]:
    call_id = _text(call.get("call_id"), "call_id")
    tool_name = _text(call.get("tool_name"), f"{call_id}.tool_name")
    schema_version = _text(call.get("schema_version"), f"{call_id}.schema_version")
    key = f"{tool_name}@{schema_version}"
    schema = registry.get(key)
    if schema is None:
        return _decision(call, "UNKNOWN_SCHEMA", "ESCALATE", "REVIEW_REQUIRED", ["SCHEMA_NOT_IN_GATE_INDEX"])

    problems = []
    if _unsafe_schema_text(schema):
        problems.append("UNSAFE_SCHEMA_TEXT")
    if _schema_drift(call, schema):
        problems.append("SCHEMA_DRIFT")
    structural = _structural_errors(call.get("arguments"), schema.get("input_schema", {}))
    problems.extend(structural)
    if _unsafe_argument_value(call.get("arguments")):
        problems.append("UNSAFE_ARGUMENT_VALUE")
    if _under_specified(schema):
        problems.append("UNDER_SPECIFIED_SCHEMA")

    if not problems:
        return _decision(call, "VALID", "ALLOW", "EXECUTE", ["SCHEMA_GATE_VALIDATED"])
    if "UNSAFE_SCHEMA_TEXT" in problems or "UNSAFE_ARGUMENT_VALUE" in problems:
        return _decision(call, "UNSAFE", "DENY", "BLOCK", sorted(set(problems + ["SCHEMA_GATE_FAIL_CLOSED"])))
    if any(item.startswith("STRUCTURAL_") for item in problems):
        return _decision(call, "STRUCTURAL_MISMATCH", "DENY", "BLOCK", sorted(set(problems)))
    if "SCHEMA_DRIFT" in problems:
        return _decision(call, "DRIFTED", "THROTTLE", "CONSTRAINED_EXECUTE", sorted(set(problems)))
    return _decision(call, "UNDER_SPECIFIED", "ESCALATE", "REVIEW_REQUIRED", sorted(set(problems)))


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC Dynamic Schema Gate Report",
        "",
        f"Generated: `{report['generated_at']}`",
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
        f"- Registry entries: `{report['registry_count']}`",
        f"- Tool calls: `{report['tool_call_count']}`",
        f"- Classification counts: `{report['classification_counts']}`",
        f"- SMERC posture counts: `{report['smerc_posture_counts']}`",
        f"- Route hint counts: `{report['route_hint_counts']}`",
        "",
        "## Evidence Boundary",
        "",
        str(report["evidence_boundary"]),
        "",
        "## Decisions",
        "",
        "| Call | Tool | Schema | Classification | Posture | Route | Reasons |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for decision in report["decisions"]:
        lines.append(
            f"| `{decision['call_id']}` | `{decision['tool_name']}` | `{decision['schema_version']}` | "
            f"`{decision['classification']}` | `{decision['smerc_posture']}` | `{decision['route_hint']}` | "
            f"`{decision['reason_codes']}` |"
        )
    lines.append("")
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], *, json_output: str | Path, markdown_output: str | Path) -> None:
    Path(json_output).parent.mkdir(parents=True, exist_ok=True)
    Path(markdown_output).parent.mkdir(parents=True, exist_ok=True)
    Path(json_output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(markdown_output).write_text(render_markdown(report), encoding="utf-8")


def _registry_by_key(rows: Any) -> Dict[str, Mapping[str, Any]]:
    registry: Dict[str, Mapping[str, Any]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise TypeError(f"schema_registry[{index}] must be an object")
        tool_name = _text(row.get("tool_name"), f"schema_registry[{index}].tool_name")
        version = _text(row.get("schema_version"), f"schema_registry[{index}].schema_version")
        schema = row.get("input_schema")
        if not isinstance(schema, dict):
            raise TypeError(f"schema_registry[{index}].input_schema must be an object")
        key = f"{tool_name}@{version}"
        if key in registry:
            raise ValueError(f"duplicate schema registry key: {key}")
        registry[key] = row
    return registry


def _structural_errors(arguments: Any, schema: Mapping[str, Any]) -> list[str]:
    if not isinstance(arguments, dict):
        return ["STRUCTURAL_ARGUMENTS_NOT_OBJECT"]
    required = schema.get("required", [])
    properties = schema.get("properties", {})
    additional = bool(schema.get("additionalProperties", True))
    errors = []
    if not isinstance(required, list) or not isinstance(properties, dict):
        return ["STRUCTURAL_SCHEMA_INVALID"]
    for field in required:
        if field not in arguments:
            errors.append(f"STRUCTURAL_MISSING_{str(field).upper()}")
    if not additional:
        unknown = sorted(set(arguments) - set(properties))
        if unknown:
            errors.append("STRUCTURAL_UNKNOWN_FIELDS")
    for field, value in arguments.items():
        if field in properties and not _matches_type(value, properties[field].get("type")):
            errors.append(f"STRUCTURAL_TYPE_MISMATCH_{field.upper()}")
    return errors


def _matches_type(value: Any, expected: Any) -> bool:
    if expected == "string":
        return isinstance(value, str)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    return True


def _schema_drift(call: Mapping[str, Any], schema: Mapping[str, Any]) -> bool:
    expected_hash = schema.get("schema_hash")
    observed_hash = call.get("observed_schema_hash")
    return isinstance(expected_hash, str) and isinstance(observed_hash, str) and expected_hash != observed_hash


def _under_specified(schema: Mapping[str, Any]) -> bool:
    input_schema = schema.get("input_schema", {})
    properties = input_schema.get("properties", {}) if isinstance(input_schema, dict) else {}
    return not properties or schema.get("review_status") != "approved"


def _unsafe_schema_text(value: Any) -> bool:
    text = json.dumps(value, sort_keys=True).lower()
    return any(term in text for term in UNSAFE_SCHEMA_TERMS)


def _unsafe_argument_value(value: Any) -> bool:
    text = json.dumps(value, sort_keys=True).lower()
    return any(term in text for term in UNSAFE_ARGUMENT_TERMS)


def _decision(
    call: Mapping[str, Any],
    classification: str,
    posture: str,
    route: str,
    reason_codes: list[str],
) -> Dict[str, Any]:
    return {
        "call_id": _text(call.get("call_id"), "call_id"),
        "tool_name": _text(call.get("tool_name"), "tool_name"),
        "schema_version": _text(call.get("schema_version"), "schema_version"),
        "classification": classification,
        "smerc_posture": posture,
        "route_hint": route,
        "reason_codes": sorted(set(reason_codes)),
        "local_only": True,
    }


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    return value.strip()


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the SMERC dynamic schema gate on metadata-only tool calls.")
    parser.add_argument("path", default="examples/dynamic_schema_gate_examples.json", nargs="?")
    parser.add_argument("--json-output", default="reports/dynamic_schema_gate_report.json")
    parser.add_argument("--markdown-output", default="reports/Dynamic_Schema_Gate_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_report(load_payload(args.path))
    write_outputs(report, json_output=args.json_output, markdown_output=args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
