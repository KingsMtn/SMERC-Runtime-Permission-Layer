from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Callable, Dict, Mapping

from reference_engine.mcp_proxy_runner import run_mcp_proxy


VERSION = "smerc.aws-mcp-enforcement-adapter.v1"
PROTOCOL_VERSION = "2025-06-18"
TOOL_NAME = "smerc_guarded_aws_call"
Executor = Callable[[str, str, Mapping[str, Any]], Mapping[str, Any]]


class AWSMCPEnforcementAdapter:
    """MCP-facing fail-closed boundary for SMERC-governed AWS tool calls."""

    def __init__(self, executor: Executor | None = None) -> None:
        self._executor = executor

    def handle(self, request: Mapping[str, Any]) -> Dict[str, Any] | None:
        if not isinstance(request, Mapping):
            return _error(None, -32600, "Request must be a JSON object.")
        request_id = request.get("id")
        if request.get("jsonrpc") != "2.0" or not isinstance(request.get("method"), str):
            return _error(request_id, -32600, "Invalid JSON-RPC request.")
        method = request["method"]
        if method.startswith("notifications/"):
            return None
        try:
            if method == "initialize":
                return _result(
                    request_id,
                    {
                        "protocolVersion": PROTOCOL_VERSION,
                        "capabilities": {"tools": {"listChanged": False}},
                        "serverInfo": {"name": "smerc-aws-enforcement-adapter", "version": VERSION},
                    },
                )
            if method == "ping":
                return _result(request_id, {})
            if method == "tools/list":
                return _result(request_id, {"tools": [_tool_definition()]})
            if method == "tools/call":
                return _result(request_id, self._call_tool(request.get("params")))
            return _error(request_id, -32601, f"Unsupported method: {method}")
        except (KeyError, TypeError, ValueError) as exc:
            return _error(request_id, -32602, str(exc))
        except Exception:
            return _error(request_id, -32603, "SMERC enforcement failed closed before AWS execution.")

    def _call_tool(self, params: Any) -> Dict[str, Any]:
        if not isinstance(params, Mapping):
            raise TypeError("tools/call params must be an object")
        if params.get("name") != TOOL_NAME:
            raise ValueError(f"tools/call name must be {TOOL_NAME}")
        arguments = params.get("arguments")
        if not isinstance(arguments, Mapping):
            raise TypeError("tools/call arguments must be an object")
        governance = arguments.get("governance_request")
        aws_call = arguments.get("aws_call")
        if not isinstance(governance, Mapping) or not isinstance(aws_call, Mapping):
            raise TypeError("governance_request and aws_call must be objects")
        server_name = _required_text(aws_call, "server_name")
        tool_name = _required_text(aws_call, "tool_name")
        tool_arguments = aws_call.get("arguments", {})
        if not isinstance(tool_arguments, Mapping):
            raise TypeError("aws_call.arguments must be an object")
        if not _is_aws_target(server_name):
            raise ValueError("aws_call.server_name must identify an AWS MCP server")
        governance_tool = governance.get("tool_call")
        governance_server = governance.get("server")
        if not isinstance(governance_tool, Mapping) or not isinstance(governance_server, Mapping):
            raise TypeError("governance_request must include server and tool_call objects")
        if governance_tool.get("tool_name") != tool_name:
            raise ValueError("AWS tool name must match governance_request.tool_call.tool_name")
        if governance_server.get("name") != server_name:
            raise ValueError("AWS server name must match governance_request.server.name")

        report = run_mcp_proxy(governance, mode="enforce", require_agent_identity=True)
        decision = report["governance_report"]["decision"]
        route = report["governance_report"]["sparta_route"]
        evidence = {
            "adapter_version": VERSION,
            "posture": decision["posture"],
            "route_state": route["route_state"],
            "replay_id": decision["replay_id"],
            "reason_codes": list(decision.get("reason_codes", [])),
            "required_controls": list(route.get("applied_controls", [])),
        }
        if decision["posture"] != "ALLOW" or not report["proxy_response"]["should_forward_tool_call"]:
            return _tool_error("SMERC did not authorize AWS execution.", evidence)
        if self._executor is None:
            return _tool_error("No trusted AWS MCP executor is configured; execution failed closed.", evidence)
        try:
            upstream_result = self._executor(server_name, tool_name, dict(tool_arguments))
        except Exception:
            return _tool_error("The trusted AWS MCP executor failed; execution state is unconfirmed.", evidence)
        if not isinstance(upstream_result, Mapping):
            return _tool_error("The trusted AWS MCP executor returned an invalid result.", evidence)
        return {
            "content": [{"type": "text", "text": json.dumps(dict(upstream_result), sort_keys=True)}],
            "structuredContent": {"aws_result": dict(upstream_result), "smerc": evidence},
            "isError": False,
        }


def _tool_definition() -> Dict[str, Any]:
    return {
        "name": TOOL_NAME,
        "title": "SMERC-Guarded AWS Call",
        "description": "Evaluate recoverability and execute an AWS MCP tool only after a fail-closed SMERC ALLOW decision.",
        "inputSchema": {
            "type": "object",
            "additionalProperties": False,
            "required": ["governance_request", "aws_call"],
            "properties": {
                "governance_request": {"type": "object"},
                "aws_call": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["server_name", "tool_name", "arguments"],
                    "properties": {
                        "server_name": {"type": "string"},
                        "tool_name": {"type": "string"},
                        "arguments": {"type": "object"},
                    },
                },
            },
        },
    }


def _is_aws_target(server_name: str) -> bool:
    lowered = server_name.lower()
    return lowered.startswith(("aws", "awslabs", "amazon")) or ".aws" in lowered


def _required_text(payload: Mapping[str, Any], field: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"aws_call.{field} must be a non-empty string")
    return value.strip()


def _tool_error(message: str, evidence: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "content": [{"type": "text", "text": message}],
        "structuredContent": {"smerc": dict(evidence)},
        "isError": True,
    }


def _result(request_id: Any, result: Mapping[str, Any]) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": dict(result)}


def _error(request_id: Any, code: int, message: str) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def serve_stdio(adapter: AWSMCPEnforcementAdapter) -> int:
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            response = _error(None, -32700, "Invalid JSON.")
        else:
            response = adapter.handle(request)
        if response is not None:
            print(json.dumps(response, separators=(",", ":")), flush=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the fail-closed SMERC AWS MCP enforcement adapter over stdio.")
    parser.parse_args()
    return serve_stdio(AWSMCPEnforcementAdapter())


if __name__ == "__main__":
    raise SystemExit(main())
