from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from reference_engine.recoverability_engine import RecoverabilityEngine


MCP_TOOL_RISK_SCANNER_VERSION = "smerc.mcp-tool-risk-scanner.v1"

HIGH_RISK_TERMS = {
    "delete",
    "destroy",
    "drop",
    "purge",
    "terminate",
    "wipe",
    "revoke",
    "disable",
    "remove",
    "rotate",
    "transfer",
    "refund",
    "payment",
    "deploy",
    "production",
    "iam",
    "admin",
    "permission",
    "secret",
    "token",
    "credential",
    "customer",
    "database",
    "bucket",
    "cluster",
}

READ_ONLY_TERMS = {
    "read",
    "get",
    "list",
    "search",
    "fetch",
    "lookup",
    "query",
    "summarize",
    "inspect",
    "describe",
}

WRITE_TERMS = {
    "create",
    "update",
    "write",
    "modify",
    "edit",
    "send",
    "post",
    "publish",
    "notify",
    "execute",
    "run",
    "restart",
    "scale",
}

SENSITIVE_TERMS = {
    "customer",
    "user",
    "email",
    "pii",
    "phi",
    "financial",
    "payment",
    "bank",
    "account",
    "credential",
    "secret",
    "token",
    "key",
}


def scan_mcp_tool_definition(payload: Mapping[str, Any], *, engine: RecoverabilityEngine | None = None) -> Dict[str, Any]:
    tool = _parse_tool(payload)
    tokens = _tokenize(_joined_tool_text(tool))
    annotations = _annotations(tool)
    operation_class = _operation_class(tool, tokens, annotations)
    signals = _risk_signals(tool, tokens, annotations, operation_class)
    action = _action_from_tool(tool, operation_class, signals)
    decision = (engine or RecoverabilityEngine()).evaluate(action)
    exposure = decision["scores"]["irreversible_exposure_score"]
    capacity = decision["scores"]["reversible_capacity_score"]
    authorization = decision["scores"]["risk_adjusted_authorization_score"]
    missing_metadata = _missing_metadata(tool, annotations)
    reason_codes = _scanner_reason_codes(tokens, annotations, operation_class, signals, decision, missing_metadata)
    return {
        "schema": MCP_TOOL_RISK_SCANNER_VERSION,
        "generated_at": _now(),
        "tool_name": tool["name"],
        "operation_class": operation_class,
        "likely_smerc_posture": decision["posture"],
        "irreversible_exposure_score": exposure,
        "reversible_capacity_score": capacity,
        "risk_adjusted_authorization_score": authorization,
        "reason_codes": reason_codes,
        "recommended_controls": _recommended_controls(decision, operation_class, missing_metadata),
        "missing_metadata": missing_metadata,
        "derived_risk_signals": signals,
        "mcp_governance_request_skeleton": _request_skeleton(tool, operation_class, signals),
        "plain_english_summary": _summary(tool, operation_class, decision, missing_metadata),
        "evidence_boundary": (
            "This scanner uses deterministic keyword, annotation, and schema heuristics to triage MCP tool definitions. "
            "It is a front-door risk scanner, not proof that a live tool call is safe or unsafe."
        ),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC MCP Tool Risk Scanner Report",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Summary",
        "",
        f"- Tool: `{report['tool_name']}`",
        f"- Operation class: `{report['operation_class']}`",
        f"- Likely SMERC posture: `{report['likely_smerc_posture']}`",
        f"- Irreversible exposure score: `{report['irreversible_exposure_score']}`",
        f"- Reversible capacity score: `{report['reversible_capacity_score']}`",
        f"- Risk-adjusted authorization score: `{report['risk_adjusted_authorization_score']}`",
        "",
        "## Reason Codes",
        "",
    ]
    lines.extend(f"- `{code}`" for code in report.get("reason_codes", []))
    lines.extend(["", "## Recommended Controls", ""])
    lines.extend(f"- `{control}`" for control in report.get("recommended_controls", []))
    lines.extend(["", "## Missing Metadata", ""])
    if report.get("missing_metadata"):
        lines.extend(f"- `{item}`" for item in report["missing_metadata"])
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Plain English",
            "",
            str(report["plain_english_summary"]),
            "",
            "## Evidence Boundary",
            "",
            str(report["evidence_boundary"]),
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], *, json_path: str | Path, markdown_path: str | Path) -> None:
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(json_path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(markdown_path).parent.mkdir(parents=True, exist_ok=True)
    Path(markdown_path).write_text(render_markdown(report), encoding="utf-8")


def _parse_tool(payload: Mapping[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise TypeError("MCP tool definition must be an object")
    if "name" not in payload:
        raise ValueError("MCP tool definition missing field: name")
    allowed = {"name", "description", "inputSchema", "annotations", "metadata"}
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise ValueError(f"MCP tool definition contains unknown field(s): {', '.join(unknown)}")
    tool = dict(payload)
    tool["name"] = _safe_text(tool["name"], "name", 128)
    tool["description"] = _safe_text(tool.get("description", ""), "description", 1024, required=False)
    for section in ("inputSchema", "annotations", "metadata"):
        value = tool.get(section, {})
        if value is None:
            value = {}
        if not isinstance(value, Mapping):
            raise TypeError(f"{section} must be an object when provided")
        tool[section] = dict(value)
    return tool


def _risk_signals(
    tool: Mapping[str, Any],
    tokens: set[str],
    annotations: Mapping[str, Any],
    operation_class: str,
) -> Dict[str, float]:
    destructive = annotations.get("destructiveHint") is True or operation_class in {"delete", "payment", "deploy"}
    read_only = annotations.get("readOnlyHint") is True or operation_class == "read"
    idempotent = annotations.get("idempotentHint") is True
    open_world = annotations.get("openWorldHint") is True
    sensitive = bool(tokens & SENSITIVE_TERMS) or _schema_mentions_sensitive(tool.get("inputSchema", {}))
    high_terms = len(tokens & HIGH_RISK_TERMS)
    write_terms = len(tokens & WRITE_TERMS)

    base = 0.16
    base += 0.28 if destructive else 0
    base += 0.18 if operation_class in {"write", "execute"} else 0
    base += 0.15 if sensitive else 0
    base += min(0.20, high_terms * 0.035)
    base += 0.08 if open_world else 0
    base -= 0.12 if read_only else 0

    reversibility = 0.86
    reversibility -= 0.52 if destructive else 0
    reversibility -= 0.16 if operation_class in {"write", "execute"} else 0
    reversibility -= 0.12 if sensitive else 0
    reversibility += 0.08 if idempotent else 0
    reversibility += 0.08 if annotations.get("supportsRollback") is True else 0

    containment = 0.72
    containment -= 0.18 if open_world else 0
    containment -= 0.12 if sensitive else 0
    containment -= 0.08 if write_terms > 0 else 0
    containment += 0.10 if annotations.get("supportsScopeLimit") is True else 0

    rollback_latency = 0.18
    rollback_latency += 0.46 if destructive else 0
    rollback_latency += 0.16 if operation_class in {"deploy", "payment"} else 0
    rollback_latency -= 0.08 if annotations.get("supportsRollback") is True else 0

    evidence_validity = 0.64
    evidence_validity += 0.10 if tool.get("description") else 0
    evidence_validity += 0.07 if tool.get("inputSchema") else 0
    evidence_validity += 0.06 if annotations else 0
    evidence_validity -= 0.12 if destructive and annotations.get("destructiveHint") is not True else 0

    anomaly = 0.10 + (0.08 if open_world else 0) + (0.06 if destructive else 0)
    impact_scope = 0.14 + (0.40 if destructive else 0) + (0.18 if sensitive else 0) + min(0.14, high_terms * 0.025)
    cancel = 0.82 - (0.42 if destructive else 0) - (0.14 if operation_class in {"deploy", "payment"} else 0)
    confidence = 0.74 + (0.08 if annotations else 0) - (0.14 if destructive and not annotations else 0)

    return {
        "base_action_risk": _clamp(base),
        "reversibility": _clamp(reversibility),
        "containment_strength": _clamp(containment),
        "rollback_latency": _clamp(rollback_latency),
        "evidence_validity": _clamp(evidence_validity),
        "anomaly_pressure": _clamp(anomaly),
        "impact_scope": _clamp(impact_scope),
        "cancel_reliability": _clamp(cancel),
        "authorization_confidence": _clamp(confidence),
    }


def _action_from_tool(tool: Mapping[str, Any], operation_class: str, signals: Mapping[str, float]) -> Dict[str, Any]:
    return {
        "action_id": f"MCP_TOOL_SCAN_{_identifier(tool['name']).upper()}",
        "description": f"Scan MCP tool definition for `{tool['name']}` before autonomous use.",
        "actor": "mcp_tool_risk_scanner",
        "tool": f"mcp.registry.{_identifier(tool['name'])}",
        "action_type": f"mcp_tool_{operation_class}",
        "base_action_risk": signals["base_action_risk"],
        "reversibility": signals["reversibility"],
        "containment_strength": signals["containment_strength"],
        "rollback_latency": signals["rollback_latency"],
        "evidence_validity": signals["evidence_validity"],
        "anomaly_pressure": signals["anomaly_pressure"],
        "impact_scope": signals["impact_scope"],
        "cancel_reliability": signals["cancel_reliability"],
        "authorization_confidence": signals["authorization_confidence"],
        "external_side_effect": operation_class != "read",
        "sensitive_data": _schema_mentions_sensitive(tool.get("inputSchema", {})) or bool(_tokenize(_joined_tool_text(tool)) & SENSITIVE_TERMS),
        "context": {"domain_profile": _domain_profile(operation_class, tool)},
    }


def _operation_class(tool: Mapping[str, Any], tokens: set[str], annotations: Mapping[str, Any]) -> str:
    name = tool["name"].lower()
    if annotations.get("readOnlyHint") is True:
        return "read"
    if annotations.get("destructiveHint") is True or tokens & {"delete", "drop", "purge", "destroy", "terminate", "wipe"}:
        return "delete"
    if tokens & {"transfer", "refund", "payment", "pay", "invoice", "settle"}:
        return "payment"
    if tokens & {"deploy", "release", "rollback", "production"}:
        return "deploy"
    if tokens & {"execute", "run", "restart", "scale", "rotate"}:
        return "execute"
    if tokens & WRITE_TERMS:
        return "write"
    if name.startswith(("get_", "list_", "search_", "read_", "fetch_")) or tokens & READ_ONLY_TERMS:
        return "read"
    return "execute"


def _scanner_reason_codes(
    tokens: set[str],
    annotations: Mapping[str, Any],
    operation_class: str,
    signals: Mapping[str, float],
    decision: Mapping[str, Any],
    missing_metadata: Iterable[str],
) -> list[str]:
    codes = set(decision.get("reason_codes", []))
    if operation_class != "read":
        codes.add("TOOL_CAN_CREATE_SIDE_EFFECTS")
    if operation_class in {"delete", "payment", "deploy"}:
        codes.add("HIGH_IMPACT_TOOL_CLASS")
    if tokens & SENSITIVE_TERMS:
        codes.add("SENSITIVE_DOMAIN_TERMS")
    if annotations.get("destructiveHint") is not True and operation_class == "delete":
        codes.add("DESTRUCTIVE_TOOL_NOT_ANNOTATED")
    if signals["reversibility"] < 0.45:
        codes.add("LOW_INFERRED_REVERSIBILITY")
    if missing_metadata:
        codes.add("MISSING_GOVERNANCE_METADATA")
    return sorted(codes)


def _recommended_controls(decision: Mapping[str, Any], operation_class: str, missing_metadata: list[str]) -> list[str]:
    controls = set(decision.get("controls", []))
    if operation_class != "read":
        controls.update({"require_human_approval", "require_scope_limit"})
    if operation_class in {"delete", "payment", "deploy"}:
        controls.update({"require_dry_run", "require_rollback_plan", "record_decision_lifecycle"})
    if missing_metadata:
        controls.add("complete_tool_governance_metadata")
    return sorted(controls)


def _missing_metadata(tool: Mapping[str, Any], annotations: Mapping[str, Any]) -> list[str]:
    missing = []
    if not tool.get("description"):
        missing.append("description")
    if not tool.get("inputSchema"):
        missing.append("inputSchema")
    for field in ("readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"):
        if field not in annotations:
            missing.append(f"annotations.{field}")
    for field in ("supportsRollback", "supportsScopeLimit"):
        if field not in annotations:
            missing.append(f"annotations.{field}")
    return missing


def _request_skeleton(tool: Mapping[str, Any], operation_class: str, signals: Mapping[str, float]) -> Dict[str, Any]:
    return {
        "schema": "smerc.mcp-tool-governance.v1",
        "mcp_request_id": f"MCP_{_identifier(tool['name']).upper()}_REVIEW",
        "agent": {"agent_id": "agent_under_review", "display_name": "Agent under review", "provider": "unknown"},
        "server": {"name": "mcp_server_under_review", "transport": "unknown", "trust_boundary": "unknown"},
        "tool_call": {
            "tool_name": tool["name"],
            "description": tool.get("description") or f"Call MCP tool {tool['name']}.",
            "operation_class": operation_class,
            "requested_capability": operation_class,
            "domain_profile": _domain_profile(operation_class, tool),
            "external_side_effect": operation_class != "read",
            "sensitive_data": bool(_tokenize(_joined_tool_text(tool)) & SENSITIVE_TERMS),
            "supports_dry_run": bool(tool["annotations"].get("supportsDryRun", False)),
            "supports_scope_limit": bool(tool["annotations"].get("supportsScopeLimit", False)),
            "supports_checkpoint": bool(tool["annotations"].get("supportsCheckpoint", False)),
            "supports_rollback": bool(tool["annotations"].get("supportsRollback", False)),
            "supports_human_approval": True,
            "requested_scope_units": 1,
            "max_scope_units": 1,
        },
        "risk_signals": dict(signals),
    }


def _summary(tool: Mapping[str, Any], operation_class: str, decision: Mapping[str, Any], missing_metadata: list[str]) -> str:
    metadata_clause = " The definition is missing governance metadata that should be supplied before pilot use." if missing_metadata else ""
    return (
        f"SMERC scanned MCP tool `{tool['name']}` as a likely `{operation_class}` operation and returned "
        f"{decision['posture']}. This should be treated as a triage result for reviewers before the tool is granted "
        f"autonomous execution authority.{metadata_clause}"
    )


def _domain_profile(operation_class: str, tool: Mapping[str, Any]) -> str:
    text = _joined_tool_text(tool).lower()
    if operation_class == "payment" or "payment" in text or "refund" in text or "transfer" in text:
        return "finance_ops"
    if "iam" in text or "identity" in text or "permission" in text or "security" in text:
        return "security_ops"
    if "deploy" in text or "github" in text or "pull request" in text:
        return "github_actions"
    if "cloud" in text or "kubernetes" in text or "cluster" in text or "bucket" in text:
        return "cloud_admin"
    if "email" in text or "customer" in text:
        return "customer_comms"
    return "it_ops"


def _annotations(tool: Mapping[str, Any]) -> Dict[str, Any]:
    return dict(tool.get("annotations", {}))


def _joined_tool_text(tool: Mapping[str, Any]) -> str:
    return " ".join(
        [
            str(tool.get("name", "")),
            str(tool.get("description", "")),
            json.dumps(tool.get("inputSchema", {}), sort_keys=True),
            json.dumps(tool.get("metadata", {}), sort_keys=True),
        ]
    )


def _schema_mentions_sensitive(schema: Mapping[str, Any]) -> bool:
    return bool(_tokenize(json.dumps(schema, sort_keys=True)) & SENSITIVE_TERMS)


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower().replace("_", " ").replace("-", " ")))


def _identifier(value: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9_.:-]+", "_", value.strip())
    return text.strip("_")[:128] or "unknown_tool"


def _safe_text(value: Any, path: str, maximum: int, *, required: bool = True) -> str:
    if value is None and not required:
        return ""
    if not isinstance(value, str):
        raise TypeError(f"{path} must be a string")
    text = value.strip()
    if required and not text:
        raise ValueError(f"{path} must be non-empty")
    if len(text) > maximum:
        raise ValueError(f"{path} must be at most {maximum} characters")
    return text


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: str | Path) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan an MCP tool definition for recoverability and autonomy risk.")
    parser.add_argument("--tool", default="examples/mcp/tool_definition_risk_examples.json")
    parser.add_argument("--select", default="delete_customer_records")
    parser.add_argument("--json-output", default="reports/mcp_tool_risk_scanner_report.json")
    parser.add_argument("--markdown-output", default="reports/MCP_Tool_Risk_Scanner_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    payload = load_json(args.tool)
    if payload.get("schema") == "smerc.mcp-tool-risk-examples.v1":
        tools = payload.get("tools", {})
        if not isinstance(tools, Mapping) or args.select not in tools:
            raise ValueError(f"--select must name one tool in {args.tool}")
        payload = tools[args.select]
    report = scan_mcp_tool_definition(payload)
    write_outputs(report, json_path=args.json_output, markdown_path=args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
