from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import re
import subprocess
import sys
from typing import Any, Callable, Dict, Mapping, Sequence
from urllib.parse import urlsplit

from reference_engine.mcp_proxy_runner import run_mcp_proxy
from reference_engine.runtime_admission_gate import evaluate_runtime_admission_gate
from integrations.github_ephemeral.github_remote_adapter import verify_github_admission_evidence


VERSION = "smerc.aws-mcp-enforcement-adapter.v1"
PROTOCOL_VERSION = "2025-06-18"
TOOL_NAME = "smerc_guarded_aws_call"
PILOT_COST_CEILING_USD = 2.0
SESSION_COST_CEILING_USD = 5.0
Executor = Callable[[str, str, Mapping[str, Any]], Mapping[str, Any]]
OAuthTokenProvider = Callable[[bool], str]


def _canonical_digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class StdioMCPExecutor:
    """One-call MCP client for an explicitly configured upstream command."""

    def __init__(self, command: Sequence[str], *, timeout_seconds: float = 30.0) -> None:
        if not command or any(not isinstance(part, str) or not part.strip() for part in command):
            raise ValueError("upstream command must contain non-empty argv entries")
        if timeout_seconds <= 0:
            raise ValueError("upstream timeout must be greater than zero")
        self._command = tuple(command)
        self._timeout_seconds = timeout_seconds

    def __call__(self, server_name: str, tool_name: str, arguments: Mapping[str, Any]) -> Mapping[str, Any]:
        del server_name  # The configured command is the sole trusted upstream boundary.
        initialize_id = "smerc-upstream-initialize"
        call_id = "smerc-upstream-call"
        requests = (
            {
                "jsonrpc": "2.0",
                "id": initialize_id,
                "method": "initialize",
                "params": {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {},
                    "clientInfo": {"name": "smerc-aws-enforcement-adapter", "version": VERSION},
                },
            },
            {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
            {
                "jsonrpc": "2.0",
                "id": call_id,
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": dict(arguments)},
            },
        )
        payload = "".join(json.dumps(item, separators=(",", ":")) + "\n" for item in requests)
        try:
            completed = subprocess.run(
                self._command,
                input=payload,
                text=True,
                capture_output=True,
                timeout=self._timeout_seconds,
                check=False,
                shell=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise RuntimeError("trusted AWS MCP upstream was unavailable") from exc
        responses = []
        for line in completed.stdout.splitlines():
            try:
                candidate = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(candidate, Mapping):
                responses.append(candidate)
        initialized = [item for item in responses if item.get("id") == initialize_id]
        if len(initialized) != 1 or initialized[0].get("jsonrpc") != "2.0" or "result" not in initialized[0]:
            raise RuntimeError("trusted AWS MCP upstream did not complete initialization")
        matching = [item for item in responses if item.get("id") == call_id]
        if len(matching) != 1 or matching[0].get("jsonrpc") != "2.0":
            raise RuntimeError("trusted AWS MCP upstream returned no matching JSON-RPC response")
        response = matching[0]
        if "error" in response:
            raise RuntimeError("trusted AWS MCP upstream returned a JSON-RPC error")
        result = response.get("result")
        if not isinstance(result, Mapping) or result.get("isError") is True:
            raise RuntimeError("trusted AWS MCP upstream returned a failed or invalid tool result")
        return dict(result)


class ManagedAWSMCPProxyExecutor(StdioMCPExecutor):
    """Trusted stdio route to the AWS managed MCP endpoint via AWS's proxy."""

    def __init__(
        self,
        proxy_command: Sequence[str],
        *,
        endpoint: str = "https://aws-mcp.us-east-1.api.aws/mcp",
        resource_region: str = "us-east-1",
        timeout_seconds: float = 30.0,
    ) -> None:
        if not proxy_command:
            raise ValueError("AWS MCP proxy command must not be empty")
        _require_reviewed_proxy_command(proxy_command)
        endpoint = _managed_aws_mcp_endpoint(endpoint)
        resource_region = _aws_region(resource_region)
        command = (*proxy_command, endpoint, "--metadata", f"AWS_REGION={resource_region}")
        super().__init__(command, timeout_seconds=timeout_seconds)


class AWSOAuthMCPExecutor:
    """Direct, bounded OAuth transport to the AWS managed MCP endpoint.

    Token acquisition and secure storage stay behind ``token_provider``. The
    executor requests one refresh after a 401 and never includes token material
    in its return value or raised errors.
    """

    def __init__(
        self,
        token_provider: OAuthTokenProvider,
        *,
        endpoint: str = "https://aws-mcp.us-east-1.api.aws/mcp",
        timeout_seconds: float = 30.0,
        max_response_bytes: int = 1_048_576,
    ) -> None:
        if not callable(token_provider):
            raise TypeError("token_provider must be callable")
        if timeout_seconds <= 0:
            raise ValueError("upstream timeout must be greater than zero")
        if max_response_bytes <= 0:
            raise ValueError("max_response_bytes must be greater than zero")
        endpoint = _managed_aws_mcp_endpoint(endpoint)
        parsed = urlsplit(endpoint)
        self._host = parsed.hostname or ""
        self._path = parsed.path
        self._token_provider = token_provider
        self._timeout_seconds = timeout_seconds
        self._max_response_bytes = max_response_bytes

    def __call__(self, server_name: str, tool_name: str, arguments: Mapping[str, Any]) -> Mapping[str, Any]:
        if server_name != "aws-mcp":
            raise RuntimeError("OAuth executor is bound only to aws-mcp")
        token = self._token(False)
        try:
            return self._exchange(token, tool_name, arguments)
        except _OAuthUnauthorized:
            refreshed = self._token(True)
            return self._exchange(refreshed, tool_name, arguments)

    def _token(self, force_refresh: bool) -> str:
        token = self._token_provider(force_refresh)
        if not isinstance(token, str) or not token.strip() or any(char.isspace() for char in token):
            raise RuntimeError("OAuth token provider returned no usable token")
        return token.strip()

    def _exchange(self, token: str, tool_name: str, arguments: Mapping[str, Any]) -> Mapping[str, Any]:
        initialize_id = "smerc-oauth-initialize"
        call_id = "smerc-oauth-call"
        initialize = {
            "jsonrpc": "2.0",
            "id": initialize_id,
            "method": "initialize",
            "params": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "smerc-aws-oauth-executor", "version": VERSION},
            },
        }
        initialized, session_id = self._post(token, initialize)
        if initialized.get("id") != initialize_id or "result" not in initialized:
            raise RuntimeError("AWS MCP OAuth endpoint did not complete initialization")
        self._post(token, {"jsonrpc": "2.0", "method": "notifications/initialized"}, session_id=session_id)
        response, _ = self._post(
            token,
            {
                "jsonrpc": "2.0",
                "id": call_id,
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": dict(arguments)},
            },
            session_id=session_id,
        )
        if response.get("id") != call_id or response.get("jsonrpc") != "2.0":
            raise RuntimeError("AWS MCP OAuth endpoint returned no matching response")
        if "error" in response:
            raise RuntimeError("AWS MCP OAuth endpoint returned a JSON-RPC error")
        result = response.get("result")
        if not isinstance(result, Mapping) or result.get("isError") is True:
            raise RuntimeError("AWS MCP OAuth endpoint returned a failed or invalid tool result")
        return dict(result)

    def _post(
        self,
        token: str,
        payload: Mapping[str, Any],
        *,
        session_id: str | None = None,
    ) -> tuple[dict[str, Any], str | None]:
        body = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "MCP-Protocol-Version": PROTOCOL_VERSION,
        }
        if session_id:
            headers["Mcp-Session-Id"] = session_id
        connection = http.client.HTTPSConnection(self._host, timeout=self._timeout_seconds)
        try:
            connection.request("POST", self._path, body=body, headers=headers)
            response = connection.getresponse()
            if response.status == 401:
                response.read()
                raise _OAuthUnauthorized
            if response.status not in (200, 202):
                response.read()
                raise RuntimeError(f"AWS MCP OAuth endpoint returned HTTP {response.status}")
            raw = response.read(self._max_response_bytes + 1)
            if len(raw) > self._max_response_bytes:
                raise RuntimeError("AWS MCP OAuth response exceeded the configured size limit")
            returned_session = response.getheader("Mcp-Session-Id") or session_id
            if not raw:
                return {}, returned_session
            return _decode_streamable_http_response(raw, response.getheader("Content-Type", "")), returned_session
        except _OAuthUnauthorized:
            raise
        except (OSError, http.client.HTTPException) as exc:
            raise RuntimeError("AWS MCP OAuth endpoint was unavailable") from exc
        finally:
            connection.close()


class OAuthTokenHelperProvider:
    """Fetch short-lived access tokens from a fixed host credential helper."""

    def __init__(
        self,
        command: Sequence[str],
        *,
        resource: str = "https://aws-mcp.us-east-1.api.aws/mcp",
        timeout_seconds: float = 15.0,
        max_output_bytes: int = 65_536,
    ) -> None:
        if not command or any(not isinstance(part, str) or not part.strip() for part in command):
            raise ValueError("token helper command must contain non-empty argv entries")
        if timeout_seconds <= 0 or max_output_bytes <= 0:
            raise ValueError("token helper limits must be greater than zero")
        self._command = tuple(command)
        self._resource = _managed_aws_mcp_endpoint(resource)
        self._timeout_seconds = timeout_seconds
        self._max_output_bytes = max_output_bytes

    def __call__(self, force_refresh: bool) -> str:
        request = json.dumps(
            {
                "version": "smerc.oauth-token-helper.v1",
                "operation": "get_access_token",
                "resource": self._resource,
                "force_refresh": bool(force_refresh),
            },
            separators=(",", ":"),
        )
        try:
            completed = subprocess.run(
                self._command,
                input=request + "\n",
                text=True,
                capture_output=True,
                timeout=self._timeout_seconds,
                check=False,
                shell=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise RuntimeError("OAuth token helper was unavailable") from exc
        if completed.returncode != 0:
            raise RuntimeError("OAuth token helper failed")
        encoded = completed.stdout.encode("utf-8")
        if len(encoded) > self._max_output_bytes:
            raise RuntimeError("OAuth token helper response exceeded the configured size limit")
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError("OAuth token helper returned invalid JSON") from exc
        if not isinstance(payload, Mapping) or payload.get("token_type") != "Bearer":
            raise RuntimeError("OAuth token helper returned an invalid token response")
        token = payload.get("access_token")
        if not isinstance(token, str) or not token.strip() or any(char.isspace() for char in token):
            raise RuntimeError("OAuth token helper returned no usable token")
        return token.strip()


class _OAuthUnauthorized(Exception):
    pass


def _decode_streamable_http_response(raw: bytes, content_type: str) -> dict[str, Any]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeError("AWS MCP OAuth endpoint returned non-UTF-8 content") from exc
    candidates = []
    if "text/event-stream" in content_type.lower():
        candidates = [line[5:].strip() for line in text.splitlines() if line.startswith("data:")]
    else:
        candidates = [text]
    for candidate in reversed(candidates):
        try:
            decoded = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(decoded, dict):
            return decoded
    raise RuntimeError("AWS MCP OAuth endpoint returned no valid JSON-RPC payload")


class AWSMCPEnforcementAdapter:
    """MCP-facing fail-closed boundary for SMERC-governed AWS tool calls."""

    def __init__(
        self,
        executor: Executor | None = None,
        *,
        approved_cost_usd: float = 0.0,
        approved_target_sha256: str | None = None,
        approver_id: str | None = None,
        required_github_admission_sha256: str | None = None,
    ) -> None:
        if not isinstance(approved_cost_usd, (int, float)) or isinstance(approved_cost_usd, bool):
            raise TypeError("approved_cost_usd must be a number")
        if approved_cost_usd < 0 or approved_cost_usd > PILOT_COST_CEILING_USD:
            raise ValueError(f"approved_cost_usd must be between 0 and {PILOT_COST_CEILING_USD}")
        if (approved_target_sha256 is None) != (approver_id is None):
            raise ValueError("approved_target_sha256 and approver_id must be configured together")
        if approved_target_sha256 is not None and not re.fullmatch(r"[0-9a-f]{64}", approved_target_sha256):
            raise ValueError("approved_target_sha256 must be a lowercase SHA-256 digest")
        if approver_id is not None and (not isinstance(approver_id, str) or not approver_id.strip()):
            raise TypeError("approver_id must be a non-empty string")
        if required_github_admission_sha256 is not None and not re.fullmatch(
            r"[0-9a-f]{64}", required_github_admission_sha256
        ):
            raise ValueError("required_github_admission_sha256 must be a lowercase SHA-256 digest")
        self._executor = executor
        self._approved_cost_usd = float(approved_cost_usd)
        self._approved_target_sha256 = approved_target_sha256
        self._approver_id = approver_id.strip() if approver_id is not None else None
        self._required_github_admission_sha256 = required_github_admission_sha256
        self._estimated_session_spend_usd = 0.0

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
        admission_payload = arguments.get("runtime_admission")
        aws_call = arguments.get("aws_call")
        github_admission_payload = arguments.get("github_admission")
        if not isinstance(admission_payload, Mapping):
            raise TypeError("runtime_admission must be an object")
        if not isinstance(governance, Mapping) or not isinstance(aws_call, Mapping):
            raise TypeError("governance_request and aws_call must be objects")
        github_admission = None
        if github_admission_payload is not None:
            if not isinstance(github_admission_payload, Mapping):
                raise TypeError("github_admission must be an object")
            github_admission = verify_github_admission_evidence(github_admission_payload)
        if self._required_github_admission_sha256 is not None:
            if github_admission is None:
                raise ValueError("github_admission is required before AWS execution")
            if github_admission["evidence_sha256"] != self._required_github_admission_sha256:
                raise ValueError("github_admission does not match the operator-approved evidence digest")
        server_name = _required_text(aws_call, "server_name")
        tool_name = _required_text(aws_call, "tool_name")
        tool_arguments = aws_call.get("arguments", {})
        if not isinstance(tool_arguments, Mapping):
            raise TypeError("aws_call.arguments must be an object")
        cost_control = aws_call.get("cost_control")
        if not isinstance(cost_control, Mapping):
            raise TypeError("aws_call.cost_control must be an object")
        estimated_cost = cost_control.get("estimated_incremental_cost_usd")
        if not isinstance(estimated_cost, (int, float)) or isinstance(estimated_cost, bool) or estimated_cost < 0:
            raise TypeError("aws_call.cost_control.estimated_incremental_cost_usd must be a non-negative number")
        cost_evidence = {
            "estimated_incremental_cost_usd": float(estimated_cost),
            "operator_approved_cost_usd": self._approved_cost_usd,
            "pilot_cost_ceiling_usd": PILOT_COST_CEILING_USD,
            "estimated_session_spend_before_usd": self._estimated_session_spend_usd,
            "session_cost_ceiling_usd": SESSION_COST_CEILING_USD,
        }
        execution_binding = {
            "server_name": server_name,
            "tool_name": tool_name,
            "arguments_sha256": _canonical_digest(dict(tool_arguments)),
        }
        if github_admission is not None:
            execution_binding["github_source"] = {
                "repository": github_admission["repository"],
                "remote_ref": github_admission["remote_ref"],
                "sealed_commit_sha": github_admission["sealed_commit_sha"],
                "admission_evidence_sha256": github_admission["evidence_sha256"],
            }
        execution_binding["target_sha256"] = _canonical_digest(execution_binding)
        if estimated_cost > PILOT_COST_CEILING_USD:
            return _tool_error("AWS execution exceeds the SMERC pilot cost ceiling.", cost_evidence)
        if estimated_cost > self._approved_cost_usd:
            return _tool_error("AWS execution may incur charges and lacks explicit owner approval.", cost_evidence)
        projected_session_spend = self._estimated_session_spend_usd + float(estimated_cost)
        cost_evidence["estimated_session_spend_after_usd"] = projected_session_spend
        if projected_session_spend >= SESSION_COST_CEILING_USD:
            return _tool_error("AWS execution would reach the SMERC session cost stop.", cost_evidence)
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

        admission = evaluate_runtime_admission_gate(admission_payload)
        if admission["decision"] != "ADMIT":
            return _tool_error(
                "SMERC runtime admission rejected AWS execution.",
                {
                    "adapter_version": VERSION,
                    "admission_decision": admission["decision"],
                    "admission_reason_codes": list(admission["reason_codes"]),
                    "failed_required_checks": list(admission["failed_required_checks"]),
                },
            )

        report = run_mcp_proxy(governance, mode="enforce", require_agent_identity=True)
        decision = report["governance_report"]["decision"]
        route = report["governance_report"]["sparta_route"]
        evidence = {
            "adapter_version": VERSION,
            "admission_decision": admission["decision"],
            "admission_reason_codes": list(admission["reason_codes"]),
            "posture": decision["posture"],
            "route_state": route["route_state"],
            "replay_id": decision["replay_id"],
            "reason_codes": list(decision.get("reason_codes", [])),
            "required_controls": list(route.get("applied_controls", [])),
            "cost_control": cost_evidence,
            "execution_binding": execution_binding,
        }
        if github_admission is not None:
            evidence["github_admission"] = {
                "repository": github_admission["repository"],
                "sealed_commit_sha": github_admission["sealed_commit_sha"],
                "evidence_sha256": github_admission["evidence_sha256"],
            }
        approval_transition = _validated_throttle_approval(
            posture=decision["posture"],
            target_sha256=execution_binding["target_sha256"],
            approved_target_sha256=self._approved_target_sha256,
            approver_id=self._approver_id,
        )
        if approval_transition is not None:
            evidence["approval_transition"] = approval_transition
        may_execute = decision["posture"] == "ALLOW" or approval_transition is not None
        if not may_execute or (
            decision["posture"] == "ALLOW" and not report["proxy_response"]["should_forward_tool_call"]
        ):
            return _tool_error("SMERC did not authorize AWS execution.", evidence)
        if self._executor is None:
            return _tool_error("No trusted AWS MCP executor is configured; execution failed closed.", evidence)
        self._estimated_session_spend_usd = projected_session_spend
        try:
            upstream_result = self._executor(server_name, tool_name, dict(tool_arguments))
        except Exception:
            return _tool_error("The trusted AWS MCP executor failed; execution state is unconfirmed.", evidence)
        if not isinstance(upstream_result, Mapping):
            return _tool_error("The trusted AWS MCP executor returned an invalid result.", evidence)
        evidence["execution_result"] = {
            "status": "succeeded",
            "result_sha256": _canonical_digest(dict(upstream_result)),
        }
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
            "required": ["runtime_admission", "governance_request", "aws_call"],
            "properties": {
                "runtime_admission": {"type": "object"},
                "governance_request": {"type": "object"},
                "github_admission": {"type": "object"},
                "aws_call": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["server_name", "tool_name", "arguments", "cost_control"],
                    "properties": {
                        "server_name": {"type": "string"},
                        "tool_name": {"type": "string"},
                        "arguments": {"type": "object"},
                        "cost_control": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["estimated_incremental_cost_usd"],
                            "properties": {
                                "estimated_incremental_cost_usd": {"type": "number", "minimum": 0},
                            },
                        },
                    },
                },
            },
        },
    }


def _is_aws_target(server_name: str) -> bool:
    lowered = server_name.lower()
    return lowered.startswith(("aws", "awslabs", "amazon")) or ".aws" in lowered


def _validated_throttle_approval(
    *,
    posture: str,
    target_sha256: str,
    approved_target_sha256: str | None,
    approver_id: str | None,
) -> Dict[str, Any] | None:
    if approved_target_sha256 is None or approver_id is None:
        return None
    if approved_target_sha256 != target_sha256:
        return None
    if posture != "THROTTLE":
        return None
    return {
        "source_posture": "THROTTLE",
        "executed_posture": "ALLOW_WITH_OWNER_APPROVAL",
        "approver_sha256": hashlib.sha256(approver_id.encode("utf-8")).hexdigest(),
        "approved_target_sha256": target_sha256,
    }


def _managed_aws_mcp_endpoint(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError("AWS managed MCP endpoint must be a non-empty string")
    endpoint = value.strip()
    parsed = urlsplit(endpoint)
    hostname = parsed.hostname or ""
    if (
        parsed.scheme != "https"
        or parsed.username is not None
        or parsed.password is not None
        or parsed.port is not None
        or parsed.path != "/mcp"
        or parsed.query
        or parsed.fragment
        or not re.fullmatch(r"aws-mcp\.[a-z]{2}(?:-gov)?-[a-z]+-\d\.api\.aws", hostname)
    ):
        raise ValueError("endpoint must be an AWS managed MCP HTTPS /mcp endpoint")
    return endpoint


def _require_reviewed_proxy_command(command: Sequence[str]) -> None:
    lowered = [part.strip().lower() for part in command if isinstance(part, str)]
    if "mcp-proxy-for-aws-cli" in lowered or any(
        part.startswith("mcp-proxy-for-aws-cli@") and part.endswith("@latest") for part in lowered
    ):
        raise ValueError("mcp-proxy-for-aws-cli must use a pinned version or reviewed installed executable")


def _aws_region(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[a-z]{2}(?:-gov)?-[a-z]+-\d", value):
        raise ValueError("resource_region must be a valid AWS Region identifier")
    return value


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
    parser.add_argument("--upstream-timeout", type=float, default=30.0)
    parser.add_argument(
        "--approved-cost-usd",
        type=float,
        default=0.0,
        help="Operator-approved per-call cost, capped at the $2 pilot ceiling; defaults to zero.",
    )
    parser.add_argument(
        "--upstream-command",
        nargs=argparse.REMAINDER,
        help="Explicit argv for a trusted AWS MCP stdio bridge; no shell parsing is used.",
    )
    parser.add_argument(
        "--managed-aws-proxy-command",
        nargs=argparse.REMAINDER,
        help="Reviewed mcp-proxy-for-aws argv; SMERC appends the validated managed endpoint and Region metadata.",
    )
    parser.add_argument("--managed-aws-endpoint", default="https://aws-mcp.us-east-1.api.aws/mcp")
    parser.add_argument("--aws-resource-region", default="us-east-1")
    args = parser.parse_args()
    if args.upstream_command and args.managed_aws_proxy_command:
        parser.error("choose either --upstream-command or --managed-aws-proxy-command")
    executor = None
    if args.managed_aws_proxy_command:
        executor = ManagedAWSMCPProxyExecutor(
            args.managed_aws_proxy_command,
            endpoint=args.managed_aws_endpoint,
            resource_region=args.aws_resource_region,
            timeout_seconds=args.upstream_timeout,
        )
    elif args.upstream_command:
        executor = StdioMCPExecutor(args.upstream_command, timeout_seconds=args.upstream_timeout)
    return serve_stdio(AWSMCPEnforcementAdapter(executor, approved_cost_usd=args.approved_cost_usd))


if __name__ == "__main__":
    raise SystemExit(main())
