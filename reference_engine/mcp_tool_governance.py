from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.recoverability_engine import RecoverabilityEngine
from reference_engine.sparta_router import SPARTA_PLAN_VERSION, route_decision


MCP_TOOL_GOVERNANCE_VERSION = "smerc.mcp-tool-governance.v1"
SIDE_EFFECT_MAP = {
    "read": "internal",
    "write": "external",
    "execute": "external",
    "deploy": "external",
    "delete": "destructive",
    "payment": "financial",
}


def evaluate_mcp_tool_call(
    payload: Mapping[str, Any],
    *,
    engine: RecoverabilityEngine | None = None,
) -> Dict[str, Any]:
    request = _parse_request(payload)
    action = _action_from_request(request)
    plan = _plan_from_request(request)
    decision = (engine or RecoverabilityEngine()).evaluate(action)
    route = route_decision(decision, plan)
    return {
        "schema": MCP_TOOL_GOVERNANCE_VERSION,
        "generated_at": _now(),
        "mcp_request_id": request["mcp_request_id"],
        "agent_id": request["agent"]["agent_id"],
        "server_name": request["server"]["name"],
        "tool_name": request["tool_call"]["tool_name"],
        "decision": decision,
        "sparta_route": route,
        "recommended_mcp_result": _recommended_result(route),
        "plain_english_summary": _summary(request, decision, route),
        "evidence_boundary": (
            "This adapter evaluates MCP tool-call metadata before execution. It does not implement MCP transport, "
            "OAuth, enterprise identity, sandboxing, prompt-injection defense, or native tool enforcement."
        ),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    decision = report["decision"]
    route = report["sparta_route"]
    lines = [
        "# SMERC MCP Tool Governance Report",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Summary",
        "",
        f"- MCP request: `{report['mcp_request_id']}`",
        f"- Agent: `{report['agent_id']}`",
        f"- MCP server: `{report['server_name']}`",
        f"- Tool: `{report['tool_name']}`",
        f"- SMERC posture: `{decision['posture']}`",
        f"- SPARTa route state: `{route['route_state']}`",
        f"- Executable: `{str(route['executable']).lower()}`",
        f"- Recommended MCP result: `{report['recommended_mcp_result']}`",
        "",
        "## Reason Codes",
        "",
    ]
    lines.extend(f"- `{code}`" for code in decision.get("reason_codes", []))
    lines.extend(
        [
            "",
            "## Controls",
            "",
        ]
    )
    lines.extend(f"- `{control}`" for control in route.get("applied_controls", []))
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


def _parse_request(payload: Mapping[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise TypeError("MCP governance request must be an object")
    if payload.get("schema") != MCP_TOOL_GOVERNANCE_VERSION:
        raise ValueError(f"schema must be {MCP_TOOL_GOVERNANCE_VERSION}")
    required = {"schema", "mcp_request_id", "agent", "server", "tool_call", "risk_signals"}
    missing = sorted(required - set(payload))
    if missing:
        raise ValueError(f"MCP governance request missing field(s): {', '.join(missing)}")
    unknown = sorted(set(payload) - required)
    if unknown:
        raise ValueError(f"MCP governance request contains unknown field(s): {', '.join(unknown)}")
    request = dict(payload)
    _safe_identifier(request["mcp_request_id"], "mcp_request_id")
    for section in ("agent", "server", "tool_call", "risk_signals"):
        if not isinstance(request[section], Mapping):
            raise TypeError(f"{section} must be an object")
        request[section] = dict(request[section])
    return request


def _action_from_request(request: Mapping[str, Any]) -> Dict[str, Any]:
    tool_call = request["tool_call"]
    signals = request["risk_signals"]
    operation_class = _text(tool_call.get("operation_class", "execute"), "tool_call.operation_class")
    return {
        "action_id": f"MCP_{request['mcp_request_id']}",
        "description": _text(tool_call.get("description", tool_call.get("tool_name")), "tool_call.description"),
        "actor": _safe_identifier(request["agent"].get("agent_id"), "agent.agent_id"),
        "tool": f"mcp.{_safe_identifier(request['server'].get('name'), 'server.name')}.{_safe_identifier(tool_call.get('tool_name'), 'tool_call.tool_name')}",
        "action_type": f"mcp_{operation_class}",
        "base_action_risk": _score(signals.get("base_action_risk"), "risk_signals.base_action_risk"),
        "reversibility": _score(signals.get("reversibility"), "risk_signals.reversibility"),
        "containment_strength": _score(signals.get("containment_strength"), "risk_signals.containment_strength"),
        "rollback_latency": _score(signals.get("rollback_latency"), "risk_signals.rollback_latency"),
        "evidence_validity": _score(signals.get("evidence_validity"), "risk_signals.evidence_validity"),
        "anomaly_pressure": _score(signals.get("anomaly_pressure"), "risk_signals.anomaly_pressure"),
        "impact_scope": _score(signals.get("impact_scope"), "risk_signals.impact_scope"),
        "cancel_reliability": _score(signals.get("cancel_reliability"), "risk_signals.cancel_reliability"),
        "authorization_confidence": _score(signals.get("authorization_confidence"), "risk_signals.authorization_confidence"),
        "external_side_effect": bool(tool_call.get("external_side_effect", operation_class != "read")),
        "sensitive_data": bool(tool_call.get("sensitive_data", False)),
        "context": {
            "domain_profile": _text(tool_call.get("domain_profile", "it_ops"), "tool_call.domain_profile"),
            "mcp_server": request["server"].get("name"),
            "mcp_tool": tool_call.get("tool_name"),
            "operation_class": operation_class,
        },
    }


def _plan_from_request(request: Mapping[str, Any]) -> Dict[str, Any]:
    tool_call = request["tool_call"]
    operation_class = _text(tool_call.get("operation_class", "execute"), "tool_call.operation_class")
    requested_scope = _positive_int(tool_call.get("requested_scope_units", 1), "tool_call.requested_scope_units")
    max_scope = _positive_int(tool_call.get("max_scope_units", max(1, requested_scope)), "tool_call.max_scope_units")
    return {
        "version": SPARTA_PLAN_VERSION,
        "plan_id": f"mcp_plan_{request['mcp_request_id']}",
        "tool": _safe_identifier(tool_call.get("tool_name"), "tool_call.tool_name"),
        "action": operation_class,
        "requested_capability": _safe_identifier(tool_call.get("requested_capability", operation_class), "tool_call.requested_capability"),
        "supports_dry_run": bool(tool_call.get("supports_dry_run", False)),
        "supports_scope_limit": bool(tool_call.get("supports_scope_limit", False)),
        "supports_checkpoint": bool(tool_call.get("supports_checkpoint", False)),
        "supports_rollback": bool(tool_call.get("supports_rollback", False)),
        "supports_human_approval": bool(tool_call.get("supports_human_approval", True)),
        "max_scope_units": max_scope,
        "requested_scope_units": requested_scope,
        "side_effect_level": SIDE_EFFECT_MAP.get(operation_class, "external"),
        "metadata": {
            "adapter": "mcp_tool_governance",
            "mcp_server": request["server"].get("name"),
            "mcp_protocol_boundary": "pre_execution_metadata_evaluation",
        },
    }


def _recommended_result(route: Mapping[str, Any]) -> str:
    state = route.get("route_state")
    if state == "EXECUTE":
        return "call_tool"
    if state == "CONSTRAINED_EXECUTE":
        return "call_tool_with_constraints"
    if state == "REVIEW_REQUIRED":
        return "require_approval_before_tool_call"
    if state == "PAUSE":
        return "pause_tool_call"
    return "block_tool_call"


def _summary(request: Mapping[str, Any], decision: Mapping[str, Any], route: Mapping[str, Any]) -> str:
    return (
        f"SMERC evaluated MCP tool `{request['tool_call']['tool_name']}` for agent `{request['agent']['agent_id']}` "
        f"and returned {decision['posture']}. SPARTa mapped that posture to `{route['route_state']}`, so an MCP "
        f"client or proxy should use `{_recommended_result(route)}` rather than blindly executing the tool call."
    )


def _score(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{path} must be a number from 0.0 through 1.0")
    if value < 0 or value > 1:
        raise ValueError(f"{path} must be from 0.0 through 1.0")
    return float(value)


def _positive_int(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{path} must be an integer")
    if value < 1 or value > 1_000_000:
        raise ValueError(f"{path} must be from 1 through 1000000")
    return value


def _safe_identifier(value: Any, path: str) -> str:
    text = _text(value, path, 128)
    if not text.replace("_", "-").replace(".", "-").replace(":", "-").replace("-", "").isalnum():
        raise ValueError(f"{path} must be a safe identifier")
    return text


def _text(value: Any, path: str, maximum: int = 256) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    if len(value) > maximum:
        raise ValueError(f"{path} must be at most {maximum} characters")
    return value.strip()


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: str | Path) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate an MCP tool call with SMERC before execution.")
    parser.add_argument("--request", default="examples/mcp/tool_call_delete_customer_records.json")
    parser.add_argument("--json-output", default="reports/mcp_tool_governance_report.json")
    parser.add_argument("--markdown-output", default="reports/MCP_Tool_Governance_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = evaluate_mcp_tool_call(load_json(args.request))
    write_outputs(report, json_path=args.json_output, markdown_path=args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
