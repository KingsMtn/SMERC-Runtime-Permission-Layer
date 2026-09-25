from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.mcp_recovery_boundary import evaluate_mcp_recovery_boundary
from reference_engine.mcp_proxy_runner import run_mcp_proxy
from reference_engine.mcp_tool_governance import MCP_TOOL_GOVERNANCE_VERSION, load_json


MCP_TRANSPORT_PROXY_VERSION = "smerc.mcp-transport-proxy.v1"
MCP_TRANSPORT_ENVELOPE_VERSION = "smerc.mcp-transport-proxy-envelope.v1"
SUPPORTED_METHOD = "tools/call"
JSON_RPC_VERSION = "2.0"


def run_mcp_transport_proxy(envelope: Mapping[str, Any]) -> Dict[str, Any]:
    request = _parse_envelope(envelope)
    recovery_boundary = _evaluate_recovery_boundary(request)
    if recovery_boundary is not None and not recovery_boundary["eligible_for_downstream_governance"]:
        return _blocked_by_recovery_boundary(request, recovery_boundary)
    proxy_report = run_mcp_proxy(
        request["governance_request"],
        mode=request["mode"],
        require_agent_identity=bool(request.get("require_agent_identity", False)),
    )
    response = _mcp_response(request, proxy_report)
    return {
        "schema": MCP_TRANSPORT_PROXY_VERSION,
        "generated_at": _now(),
        "proxy_request_id": request["proxy_request_id"],
        "mode": request["mode"],
        "require_agent_identity": bool(request.get("require_agent_identity", False)),
        "jsonrpc_request_id": request["mcp_jsonrpc_request"]["id"],
        "mcp_method": request["mcp_jsonrpc_request"]["method"],
        "tool_name": request["governance_request"]["tool_call"]["tool_name"],
        "recovery_boundary": recovery_boundary,
        "proxy_report": proxy_report,
        "mcp_jsonrpc_response": response,
        "transport_summary": _summary(proxy_report, response),
        "evidence_boundary": (
            "MCP Transport Proxy v1 is a local JSON-RPC-style reference sample. It demonstrates how SMERC can sit "
            "between an MCP-style tools/call request and execution. It does not implement network transport, MCP "
            "session negotiation, OAuth, identity brokering, sandboxing, native tool execution, or production MCP compliance."
        ),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    if report["proxy_report"] is None:
        boundary = report["recovery_boundary"]
        return "\n".join([
            "# SMERC MCP Transport Proxy Report", "", "## Transport Decision", "",
            f"- Proxy request: `{report['proxy_request_id']}`",
            f"- Mode: `{report['mode']}`",
            f"- Tool: `{report['tool_name']}`",
            "- Forwarded: `false`",
            f"- Recovery boundary: `{boundary['boundary_state']}`",
            f"- Maximum recommended posture: `{boundary['max_recommended_posture']}`",
            "", "## Summary", "", str(report["transport_summary"]), "",
            "## Evidence Boundary", "", str(report["evidence_boundary"]), "",
        ])
    proxy = report["proxy_report"]["proxy_response"]
    response = report["mcp_jsonrpc_response"]
    forwarded = "error" not in response
    lines = [
        "# SMERC MCP Transport Proxy Report",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Transport Decision",
        "",
        f"- Proxy request: `{report['proxy_request_id']}`",
        f"- Mode: `{report['mode']}`",
        f"- Agent identity required: `{str(report['require_agent_identity']).lower()}`",
        f"- JSON-RPC request ID: `{report['jsonrpc_request_id']}`",
        f"- MCP method: `{report['mcp_method']}`",
        f"- Tool: `{report['tool_name']}`",
        f"- Proxy action: `{proxy['proxy_action']}`",
        f"- Forwarded: `{str(forwarded).lower()}`",
        f"- SMERC posture: `{proxy['decision_reference']['posture']}`",
        f"- SPARTa route: `{proxy['decision_reference']['route_state']}`",
        "",
        "## JSON-RPC Response Shape",
        "",
        "```json",
        json.dumps(response, indent=2, sort_keys=True),
        "```",
        "",
        "## Summary",
        "",
        str(report["transport_summary"]),
        "",
        "## Evidence Boundary",
        "",
        str(report["evidence_boundary"]),
        "",
    ]
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], *, json_path: str | Path, markdown_path: str | Path) -> None:
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(json_path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(markdown_path).parent.mkdir(parents=True, exist_ok=True)
    Path(markdown_path).write_text(render_markdown(report), encoding="utf-8")


def _mcp_response(request: Mapping[str, Any], proxy_report: Mapping[str, Any]) -> Dict[str, Any]:
    jsonrpc_request = request["mcp_jsonrpc_request"]
    proxy_response = proxy_report["proxy_response"]
    if proxy_response["should_forward_tool_call"]:
        result = dict(request.get("simulated_tool_result") or {})
        if not result:
            result = {
                "content": [
                    {
                        "type": "text",
                        "text": "Simulated tool call forwarded by SMERC local transport proxy.",
                    }
                ],
                "isError": False,
            }
        result["smerc_proxy"] = {
            "mode": proxy_report["mode"],
            "proxy_action": proxy_response["proxy_action"],
            "posture": proxy_response["decision_reference"]["posture"],
            "route_state": proxy_response["decision_reference"]["route_state"],
            "replay_id": proxy_response["decision_reference"]["replay_id"],
        }
        return {
            "jsonrpc": JSON_RPC_VERSION,
            "id": jsonrpc_request["id"],
            "result": result,
        }
    return {
        "jsonrpc": JSON_RPC_VERSION,
        "id": jsonrpc_request["id"],
        "error": {
            "code": -32070,
            "message": "SMERC proxy did not forward the MCP tool call.",
            "data": {
                "proxy_action": proxy_response["proxy_action"],
                "posture": proxy_response["decision_reference"]["posture"],
                "route_state": proxy_response["decision_reference"]["route_state"],
                "replay_id": proxy_response["decision_reference"]["replay_id"],
                "reason_codes": list(proxy_report["governance_report"]["decision"].get("reason_codes", [])),
                "proxy_instructions": list(proxy_response["proxy_instructions"]),
            },
        },
    }


def _evaluate_recovery_boundary(request: Mapping[str, Any]) -> Dict[str, Any] | None:
    required = bool(request.get("require_recovery_boundary", False))
    supplied = request.get("recovery_boundary")
    if not required and supplied is None:
        return None
    if supplied is None:
        supplied = _boundary_envelope_from_request(request, recovery_capability=None)
    else:
        _validate_boundary_binding(request, supplied)
    return evaluate_mcp_recovery_boundary(supplied, now_ms=request["recovery_now_ms"])


def _validate_boundary_binding(request: Mapping[str, Any], supplied: Mapping[str, Any]) -> None:
    governance = request["governance_request"]
    tool = governance["tool_call"]
    expected = {
        "request_id": governance["mcp_request_id"],
        "server_name": governance["server"]["name"],
        "tool_name": tool["tool_name"],
        "operation": tool.get("operation_class", "execute"),
        "requested_scope_units": tool.get("requested_scope_units", 1),
    }
    mismatches = [field for field, value in expected.items() if supplied.get(field) != value]
    if mismatches:
        raise ValueError(
            "recovery_boundary must match governance_request field(s): " + ", ".join(sorted(mismatches))
        )


def _boundary_envelope_from_request(
    request: Mapping[str, Any], *, recovery_capability: Mapping[str, Any] | None
) -> Dict[str, Any]:
    governance = request["governance_request"]
    tool = governance["tool_call"]
    value = {
        "version": "smerc.mcp-recovery-boundary.v1",
        "request_id": governance["mcp_request_id"],
        "server_name": governance["server"]["name"],
        "tool_name": tool["tool_name"],
        "operation": tool.get("operation_class", "execute"),
        "environment": "unspecified",
        "requested_scope_units": tool.get("requested_scope_units", 1),
        "requested_mutations": 0 if tool.get("operation_class") == "read" else 1,
        "max_acceptable_rollback_latency_seconds": 0,
    }
    if recovery_capability is not None:
        value["recovery_capability"] = recovery_capability
    return value


def _blocked_by_recovery_boundary(
    request: Mapping[str, Any], boundary: Mapping[str, Any]
) -> Dict[str, Any]:
    response = {
        "jsonrpc": JSON_RPC_VERSION,
        "id": request["mcp_jsonrpc_request"]["id"],
        "error": {
            "code": -32071,
            "message": "SMERC recovery boundary rejected the MCP tool call before governance routing.",
            "data": {
                "boundary_state": boundary["boundary_state"],
                "max_recommended_posture": boundary["max_recommended_posture"],
                "reason_codes": list(boundary["reason_codes"]),
                "authority_effect": "NONE",
            },
        },
    }
    return {
        "schema": MCP_TRANSPORT_PROXY_VERSION,
        "generated_at": _now(),
        "proxy_request_id": request["proxy_request_id"],
        "mode": request["mode"],
        "require_agent_identity": bool(request.get("require_agent_identity", False)),
        "jsonrpc_request_id": request["mcp_jsonrpc_request"]["id"],
        "mcp_method": request["mcp_jsonrpc_request"]["method"],
        "tool_name": request["governance_request"]["tool_call"]["tool_name"],
        "recovery_boundary": dict(boundary),
        "proxy_report": None,
        "mcp_jsonrpc_response": response,
        "transport_summary": (
            "The recovery boundary stopped this MCP call before normal Runtime Assurance routing. "
            "No tool execution or simulated forwarding occurred."
        ),
        "evidence_boundary": (
            "A recovery-boundary result is pre-admission evidence, not authorization, native MCP transport, "
            "or independent proof that an external recovery mechanism works."
        ),
    }


def _parse_envelope(envelope: Mapping[str, Any]) -> Dict[str, Any]:
    if not isinstance(envelope, Mapping):
        raise TypeError("MCP transport proxy envelope must be an object")
    required = {
        "schema",
        "proxy_request_id",
        "mode",
        "mcp_jsonrpc_request",
        "governance_request",
    }
    missing = sorted(required - set(envelope))
    if missing:
        raise ValueError(f"MCP transport proxy envelope missing field(s): {', '.join(missing)}")
    allowed = required | {
        "simulated_tool_result", "require_agent_identity", "require_recovery_boundary",
        "recovery_boundary", "recovery_now_ms",
    }
    unknown = sorted(set(envelope) - allowed)
    if unknown:
        raise ValueError(f"MCP transport proxy envelope contains unknown field(s): {', '.join(unknown)}")
    if envelope["schema"] != MCP_TRANSPORT_ENVELOPE_VERSION:
        raise ValueError(f"schema must be {MCP_TRANSPORT_ENVELOPE_VERSION}")
    request = dict(envelope)
    _safe_identifier(request["proxy_request_id"], "proxy_request_id")
    if request["mode"] not in {"shadow", "enforce"}:
        raise ValueError("mode must be shadow or enforce")
    if not isinstance(request["mcp_jsonrpc_request"], Mapping):
        raise TypeError("mcp_jsonrpc_request must be an object")
    if not isinstance(request["governance_request"], Mapping):
        raise TypeError("governance_request must be an object")
    request["mcp_jsonrpc_request"] = dict(request["mcp_jsonrpc_request"])
    request["governance_request"] = dict(request["governance_request"])
    _validate_jsonrpc_call(request["mcp_jsonrpc_request"], request["governance_request"])
    if "simulated_tool_result" in request and not isinstance(request["simulated_tool_result"], Mapping):
        raise TypeError("simulated_tool_result must be an object")
    if "require_recovery_boundary" in request and not isinstance(request["require_recovery_boundary"], bool):
        raise TypeError("require_recovery_boundary must be a boolean")
    if "recovery_boundary" in request and not isinstance(request["recovery_boundary"], Mapping):
        raise TypeError("recovery_boundary must be an object")
    if request.get("require_recovery_boundary") or "recovery_boundary" in request:
        now_ms = request.get("recovery_now_ms")
        if isinstance(now_ms, bool) or not isinstance(now_ms, int) or now_ms < 0:
            raise ValueError("recovery_now_ms must be a non-negative integer when recovery boundary is enabled")
    return request


def _validate_jsonrpc_call(jsonrpc_request: Mapping[str, Any], governance_request: Mapping[str, Any]) -> None:
    required = {"jsonrpc", "id", "method", "params"}
    missing = sorted(required - set(jsonrpc_request))
    if missing:
        raise ValueError(f"mcp_jsonrpc_request missing field(s): {', '.join(missing)}")
    unknown = sorted(set(jsonrpc_request) - required)
    if unknown:
        raise ValueError(f"mcp_jsonrpc_request contains unknown field(s): {', '.join(unknown)}")
    if jsonrpc_request["jsonrpc"] != JSON_RPC_VERSION:
        raise ValueError("mcp_jsonrpc_request.jsonrpc must be 2.0")
    if jsonrpc_request["method"] != SUPPORTED_METHOD:
        raise ValueError(f"mcp_jsonrpc_request.method must be {SUPPORTED_METHOD}")
    if not isinstance(jsonrpc_request["id"], (str, int)) or isinstance(jsonrpc_request["id"], bool):
        raise TypeError("mcp_jsonrpc_request.id must be a string or integer")
    if not isinstance(jsonrpc_request["params"], Mapping):
        raise TypeError("mcp_jsonrpc_request.params must be an object")
    params = jsonrpc_request["params"]
    if sorted(set(params) - {"name", "arguments"}):
        raise ValueError("mcp_jsonrpc_request.params may only contain name and arguments")
    if governance_request.get("schema") != MCP_TOOL_GOVERNANCE_VERSION:
        raise ValueError(f"governance_request.schema must be {MCP_TOOL_GOVERNANCE_VERSION}")
    tool_call = governance_request.get("tool_call")
    if not isinstance(tool_call, Mapping):
        raise TypeError("governance_request.tool_call must be an object")
    if params.get("name") != tool_call.get("tool_name"):
        raise ValueError("mcp_jsonrpc_request.params.name must match governance_request.tool_call.tool_name")
    if "arguments" in params and not isinstance(params["arguments"], Mapping):
        raise TypeError("mcp_jsonrpc_request.params.arguments must be an object")


def _summary(proxy_report: Mapping[str, Any], response: Mapping[str, Any]) -> str:
    proxy_response = proxy_report["proxy_response"]
    if "error" in response:
        return (
            f"SMERC returned {proxy_response['decision_reference']['posture']} and the transport proxy produced "
            f"JSON-RPC error {response['error']['code']} instead of forwarding the tool call."
        )
    return (
        f"SMERC returned {proxy_response['decision_reference']['posture']} and the transport proxy forwarded a "
        f"simulated JSON-RPC result with replay evidence attached."
    )


def _safe_identifier(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    text = value.strip()
    if len(text) > 128:
        raise ValueError(f"{path} must be at most 128 characters")
    if not text.replace("_", "-").replace(".", "-").replace(":", "-").replace("-", "").isalnum():
        raise ValueError(f"{path} must be a safe identifier")
    return text


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a local JSON-RPC-style MCP transport proxy sample.")
    parser.add_argument("--envelope", default="examples/mcp/transport_proxy_delete_customer_records.json")
    parser.add_argument("--require-agent-identity", action="store_true")
    parser.add_argument("--json-output", default="reports/mcp_transport_proxy_report.json")
    parser.add_argument("--markdown-output", default="reports/MCP_Transport_Proxy_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    envelope = load_json(args.envelope)
    if args.require_agent_identity:
        envelope["require_agent_identity"] = True
    report = run_mcp_transport_proxy(envelope)
    write_outputs(report, json_path=args.json_output, markdown_path=args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
