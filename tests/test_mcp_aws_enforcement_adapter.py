import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from reference_engine.mcp_aws_enforcement_adapter import (
    AWSMCPEnforcementAdapter,
    AWSOAuthMCPExecutor,
    ManagedAWSMCPProxyExecutor,
    OAuthTokenHelperProvider,
    StdioMCPExecutor,
    TOOL_NAME,
)
from reference_engine.ephemeral_execution_envelope import canonical_digest


ROOT = Path(__file__).resolve().parents[1]


def governance_request():
    payload = json.loads((ROOT / "examples/mcp/tool_call_search_docs.json").read_text(encoding="utf-8"))
    payload["server"] = {
        "name": "awslabs.aws-documentation-mcp-server",
        "transport": "streamable-http",
        "trust_boundary": "aws-managed-mcp",
    }
    payload["tool_call"]["tool_name"] = "search_documentation"
    payload["agent_identity"]["authorized_tool_families"] = ["awslabs"]
    return payload


def call_request(governance=None):
    governance = governance or governance_request()
    return {
        "jsonrpc": "2.0",
        "id": 7,
        "method": "tools/call",
        "params": {
            "name": TOOL_NAME,
            "arguments": {
                "runtime_admission": {
                    "version": "smerc.runtime-admission-input.v1",
                    "request_id": "aws-mcp-test-001",
                    "checks": {
                        "identity_valid": True,
                        "session_scope_valid": True,
                        "typed_contract_valid": True,
                        "attestation_valid": True,
                        "least_privilege_confirmed": True,
                        "object_shape_expected": True,
                    },
                },
                "governance_request": governance,
                "aws_call": {
                    "server_name": governance["server"]["name"],
                    "tool_name": governance["tool_call"]["tool_name"],
                    "arguments": {"search_phrase": "Lambda rollback"},
                    "cost_control": {"estimated_incremental_cost_usd": 0.0},
                },
            },
        },
    }


def github_admission():
    material = {
        "version": "smerc.github-admission-evidence.v1",
        "repository": "KingsMtn/SMERC-Runtime-Permission-Layer",
        "envelope_id": "smerc-ee-0123456789abcdef0123",
        "envelope_sha256": "a" * 64,
        "remote_ref": "refs/heads/smerc-ephemeral/codex/aws-001",
        "sealed_commit_sha": "b" * 40,
        "active_ruleset_ids": ["7"],
        "required_checks": ["unittest"],
        "check_conclusions": {"unittest": "success"},
        "admitted": True,
        "authenticity_boundary": "Authenticated API observation; not a GitHub-signed attestation.",
    }
    return {**material, "evidence_sha256": canonical_digest(material)}


class AWSMCPEnforcementAdapterTests(unittest.TestCase):
    def test_oauth_executor_binds_session_and_returns_matching_tool_result(self):
        responses = [
            _HTTPResponse(200, {"jsonrpc": "2.0", "id": "smerc-oauth-initialize", "result": {}}, "session-1"),
            _HTTPResponse(202, None),
            _HTTPResponse(
                200,
                {
                    "jsonrpc": "2.0",
                    "id": "smerc-oauth-call",
                    "result": {"content": [{"type": "text", "text": "37 regions"}], "isError": False},
                },
            ),
        ]
        connections = []

        def connection_factory(*args, **kwargs):
            connection = _HTTPSConnection(responses, *args, **kwargs)
            connections.append(connection)
            return connection

        with patch("reference_engine.mcp_aws_enforcement_adapter.http.client.HTTPSConnection", connection_factory):
            result = AWSOAuthMCPExecutor(lambda refresh: "secret-token")("aws-mcp", "list_regions", {})

        self.assertFalse(result["isError"])
        requests = [request for connection in connections for request in connection.requests]
        self.assertEqual(len(requests), 3)
        self.assertEqual(requests[1][3]["Mcp-Session-Id"], "session-1")
        self.assertEqual(requests[2][3]["Mcp-Session-Id"], "session-1")
        self.assertTrue(all(request[3]["Authorization"] == "Bearer secret-token" for request in requests))

    def test_oauth_executor_refreshes_once_after_unauthorized(self):
        responses = [
            _HTTPResponse(401, None),
            _HTTPResponse(200, {"jsonrpc": "2.0", "id": "smerc-oauth-initialize", "result": {}}),
            _HTTPResponse(202, None),
            _HTTPResponse(
                200,
                {"jsonrpc": "2.0", "id": "smerc-oauth-call", "result": {"content": [], "isError": False}},
            ),
        ]
        refreshes = []

        def token_provider(force_refresh):
            refreshes.append(force_refresh)
            return "refreshed" if force_refresh else "expired"

        with patch(
            "reference_engine.mcp_aws_enforcement_adapter.http.client.HTTPSConnection",
            lambda *args, **kwargs: _HTTPSConnection(responses, *args, **kwargs),
        ):
            result = AWSOAuthMCPExecutor(token_provider)("aws-mcp", "list_regions", {})

        self.assertFalse(result["isError"])
        self.assertEqual(refreshes, [False, True])

    def test_oauth_executor_rejects_untrusted_endpoint_and_server(self):
        with self.assertRaises(ValueError):
            AWSOAuthMCPExecutor(lambda refresh: "token", endpoint="https://example.com/mcp")
        executor = AWSOAuthMCPExecutor(lambda refresh: "token")
        with self.assertRaisesRegex(RuntimeError, "bound only"):
            executor("other", "list_regions", {})

    def test_token_helper_uses_stdin_contract_and_returns_only_access_token(self):
        script = (
            "import json,sys; request=json.loads(sys.stdin.read()); "
            "assert request['operation']=='get_access_token'; "
            "assert request['force_refresh'] is True; "
            "print(json.dumps({'token_type':'Bearer','access_token':'short-lived-token'}))"
        )
        provider = OAuthTokenHelperProvider([sys.executable, "-c", script])

        self.assertEqual(provider(True), "short-lived-token")

    def test_token_helper_failure_never_exposes_helper_output(self):
        script = "import sys; print('secret diagnostic'); sys.exit(1)"
        provider = OAuthTokenHelperProvider([sys.executable, "-c", script])

        with self.assertRaisesRegex(RuntimeError, "helper failed") as context:
            provider(False)
        self.assertNotIn("secret diagnostic", str(context.exception))

    def test_required_github_admission_binds_commit_to_aws_receipt(self):
        request = call_request()
        admission = github_admission()
        request["params"]["arguments"]["github_admission"] = admission
        calls = []
        adapter = AWSMCPEnforcementAdapter(
            lambda *args: calls.append(args) or {"regions": 37},
            required_github_admission_sha256=admission["evidence_sha256"],
        )

        response = adapter.handle(request)

        self.assertFalse(response["result"]["isError"])
        self.assertEqual(len(calls), 1)
        evidence = response["result"]["structuredContent"]["smerc"]
        self.assertEqual(evidence["execution_binding"]["github_source"]["sealed_commit_sha"], "b" * 40)
        self.assertEqual(evidence["github_admission"]["evidence_sha256"], admission["evidence_sha256"])

    def test_missing_or_unapproved_github_admission_never_reaches_aws(self):
        calls = []
        admission = github_admission()
        adapter = AWSMCPEnforcementAdapter(
            lambda *args: calls.append(args),
            required_github_admission_sha256=admission["evidence_sha256"],
        )
        missing = adapter.handle(call_request())
        self.assertEqual(missing["error"]["code"], -32602)

        request = call_request()
        request["params"]["arguments"]["github_admission"] = admission
        other = AWSMCPEnforcementAdapter(
            lambda *args: calls.append(args), required_github_admission_sha256="f" * 64
        ).handle(request)
        self.assertEqual(other["error"]["code"], -32602)
        self.assertEqual(calls, [])

    def test_tampered_github_admission_never_reaches_aws(self):
        calls = []
        admission = github_admission()
        admission["sealed_commit_sha"] = "c" * 40
        request = call_request()
        request["params"]["arguments"]["github_admission"] = admission

        response = AWSMCPEnforcementAdapter(
            lambda *args: calls.append(args),
            required_github_admission_sha256=admission["evidence_sha256"],
        ).handle(request)

        self.assertEqual(response["error"]["code"], -32603)
        self.assertEqual(calls, [])

    def test_exposes_native_mcp_tool(self):
        adapter = AWSMCPEnforcementAdapter()
        initialized = adapter.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        listed = adapter.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})

        self.assertEqual(initialized["result"]["serverInfo"]["name"], "smerc-aws-enforcement-adapter")
        self.assertEqual(listed["result"]["tools"][0]["name"], TOOL_NAME)

    def test_stdio_server_handles_initialize_and_tool_discovery(self):
        requests = "\n".join(
            json.dumps(item)
            for item in (
                {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            )
        ) + "\n"
        result = subprocess.run(
            [sys.executable, "-m", "reference_engine.mcp_aws_enforcement_adapter"],
            cwd=ROOT,
            input=requests,
            text=True,
            capture_output=True,
            check=False,
        )
        responses = [json.loads(line) for line in result.stdout.splitlines()]

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(responses[0]["result"]["serverInfo"]["name"], "smerc-aws-enforcement-adapter")
        self.assertEqual(responses[1]["result"]["tools"][0]["name"], TOOL_NAME)

    def test_allow_executes_only_through_trusted_executor(self):
        calls = []

        def executor(server, tool, arguments):
            calls.append((server, tool, arguments))
            return {"matches": 3}

        response = AWSMCPEnforcementAdapter(executor).handle(call_request())

        self.assertFalse(response["result"]["isError"])
        self.assertEqual(len(calls), 1)
        self.assertEqual(response["result"]["structuredContent"]["smerc"]["posture"], "ALLOW")
        self.assertEqual(response["result"]["structuredContent"]["smerc"]["admission_decision"], "ADMIT")

    def test_success_evidence_binds_exact_target_and_result(self):
        first = AWSMCPEnforcementAdapter(lambda *args: {"regions": 37}).handle(call_request())
        second = AWSMCPEnforcementAdapter(lambda *args: {"regions": 37}).handle(call_request())

        first_evidence = first["result"]["structuredContent"]["smerc"]
        second_evidence = second["result"]["structuredContent"]["smerc"]
        self.assertEqual(first_evidence["execution_binding"], second_evidence["execution_binding"])
        self.assertEqual(first_evidence["execution_result"], second_evidence["execution_result"])
        self.assertEqual(first_evidence["execution_result"]["status"], "succeeded")
        self.assertRegex(first_evidence["execution_binding"]["target_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(first_evidence["execution_result"]["result_sha256"], r"^[0-9a-f]{64}$")

    def test_argument_mutation_changes_execution_binding(self):
        original = call_request()
        changed = call_request()
        changed["params"]["arguments"]["aws_call"]["arguments"] = {"search_phrase": "S3 rollback"}

        original_result = AWSMCPEnforcementAdapter(lambda *args: {"ok": True}).handle(original)
        changed_result = AWSMCPEnforcementAdapter(lambda *args: {"ok": True}).handle(changed)

        original_binding = original_result["result"]["structuredContent"]["smerc"]["execution_binding"]
        changed_binding = changed_result["result"]["structuredContent"]["smerc"]["execution_binding"]
        self.assertNotEqual(original_binding["arguments_sha256"], changed_binding["arguments_sha256"])
        self.assertNotEqual(original_binding["target_sha256"], changed_binding["target_sha256"])

    def test_failed_runtime_admission_never_reaches_executor(self):
        request = call_request()
        request["params"]["arguments"]["runtime_admission"]["checks"]["least_privilege_confirmed"] = False
        calls = []

        response = AWSMCPEnforcementAdapter(lambda *args: calls.append(args)).handle(request)

        self.assertTrue(response["result"]["isError"])
        self.assertEqual(response["result"]["structuredContent"]["smerc"]["admission_decision"], "REJECT")
        self.assertEqual(calls, [])

    def test_missing_runtime_admission_is_rejected(self):
        request = call_request()
        del request["params"]["arguments"]["runtime_admission"]

        response = AWSMCPEnforcementAdapter(lambda *args: {}).handle(request)

        self.assertEqual(response["error"]["code"], -32602)
        self.assertIn("runtime_admission", response["error"]["message"])

    def test_missing_executor_fails_closed(self):
        response = AWSMCPEnforcementAdapter().handle(call_request())

        self.assertTrue(response["result"]["isError"])
        self.assertIn("failed closed", response["result"]["content"][0]["text"])

    def test_unknown_cost_fails_closed(self):
        request = call_request()
        del request["params"]["arguments"]["aws_call"]["cost_control"]

        response = AWSMCPEnforcementAdapter(lambda *args: {}).handle(request)

        self.assertEqual(response["error"]["code"], -32602)
        self.assertIn("cost_control", response["error"]["message"])

    def test_positive_cost_requires_owner_approval(self):
        request = call_request()
        request["params"]["arguments"]["aws_call"]["cost_control"]["estimated_incremental_cost_usd"] = 0.01
        calls = []

        response = AWSMCPEnforcementAdapter(lambda *args: calls.append(args)).handle(request)

        self.assertTrue(response["result"]["isError"])
        self.assertIn("owner approval", response["result"]["content"][0]["text"])
        self.assertEqual(calls, [])

    def test_cost_above_pilot_ceiling_is_blocked_even_when_approved(self):
        request = call_request()
        cost_control = request["params"]["arguments"]["aws_call"]["cost_control"]
        cost_control.update({"estimated_incremental_cost_usd": 2.01})
        calls = []

        response = AWSMCPEnforcementAdapter(lambda *args: calls.append(args)).handle(request)

        self.assertTrue(response["result"]["isError"])
        self.assertIn("cost ceiling", response["result"]["content"][0]["text"])
        self.assertEqual(calls, [])

    def test_trusted_operator_can_approve_cost_within_ceiling(self):
        request = call_request()
        request["params"]["arguments"]["aws_call"]["cost_control"]["estimated_incremental_cost_usd"] = 0.01
        calls = []

        response = AWSMCPEnforcementAdapter(
            lambda *args: calls.append(args) or {"ok": True},
            approved_cost_usd=0.01,
        ).handle(request)

        self.assertFalse(response["result"]["isError"])
        self.assertEqual(len(calls), 1)

    def test_operator_cannot_configure_approval_above_pilot_ceiling(self):
        with self.assertRaisesRegex(ValueError, "between 0"):
            AWSMCPEnforcementAdapter(lambda *args: {}, approved_cost_usd=2.01)

    def test_repeated_small_calls_stop_before_five_dollar_session_total(self):
        request = call_request()
        request["params"]["arguments"]["aws_call"]["cost_control"]["estimated_incremental_cost_usd"] = 1.0
        calls = []
        adapter = AWSMCPEnforcementAdapter(
            lambda *args: calls.append(args) or {"ok": True},
            approved_cost_usd=1.0,
        )

        responses = [adapter.handle(request) for _ in range(5)]

        self.assertTrue(all(not response["result"]["isError"] for response in responses[:4]))
        self.assertTrue(responses[4]["result"]["isError"])
        self.assertIn("session cost stop", responses[4]["result"]["content"][0]["text"])
        self.assertEqual(len(calls), 4)

    def test_non_allow_never_reaches_executor(self):
        governance = governance_request()
        governance["risk_signals"]["reversibility"] = 0.0
        governance["risk_signals"]["containment_strength"] = 0.0
        governance["risk_signals"]["impact_scope"] = 1.0
        calls = []
        response = AWSMCPEnforcementAdapter(lambda *args: calls.append(args)).handle(call_request(governance))

        self.assertTrue(response["result"]["isError"])
        self.assertNotEqual(response["result"]["structuredContent"]["smerc"]["posture"], "ALLOW")
        self.assertEqual(calls, [])

    def test_mismatched_tool_name_is_rejected_before_execution(self):
        request = call_request()
        request["params"]["arguments"]["aws_call"]["tool_name"] = "delete_bucket"
        response = AWSMCPEnforcementAdapter(lambda *args: {}).handle(request)

        self.assertEqual(response["error"]["code"], -32602)
        self.assertIn("must match", response["error"]["message"])

    def test_non_aws_target_is_rejected(self):
        request = call_request()
        request["params"]["arguments"]["aws_call"]["server_name"] = "untrusted-tools"
        response = AWSMCPEnforcementAdapter(lambda *args: {}).handle(request)

        self.assertEqual(response["error"]["code"], -32602)
        self.assertIn("AWS MCP server", response["error"]["message"])

    def test_executor_failure_returns_tool_error_without_claiming_success(self):
        def failed_executor(*args):
            raise RuntimeError("upstream unavailable")

        response = AWSMCPEnforcementAdapter(failed_executor).handle(call_request())

        self.assertTrue(response["result"]["isError"])
        self.assertIn("unconfirmed", response["result"]["content"][0]["text"])

    def test_stdio_executor_forwards_matching_tool_result(self):
        script = (
            "import json,sys; "
            "requests=[json.loads(line) for line in sys.stdin if line.strip()]; "
            "init=next(item for item in requests if item.get('method')=='initialize'); "
            "call=next(item for item in requests if item.get('method')=='tools/call'); "
            "print(json.dumps({'jsonrpc':'2.0','id':init['id'],'result':{'protocolVersion':'2025-06-18'}})); "
            "print(json.dumps({'jsonrpc':'2.0','id':call['id'],'result':"
            "{'content':[{'type':'text','text':'37 regions'}],'isError':False}}))"
        )
        executor = StdioMCPExecutor([sys.executable, "-c", script], timeout_seconds=5)

        result = executor("aws-mcp", "list_regions", {})

        self.assertFalse(result["isError"])
        self.assertEqual(result["content"][0]["text"], "37 regions")

    def test_stdio_executor_fails_closed_on_mismatched_response_id(self):
        script = (
            "import json; "
            "print(json.dumps({'jsonrpc':'2.0','id':'smerc-upstream-initialize','result':{}})); "
            "print(json.dumps({'jsonrpc':'2.0','id':'wrong','result':{}}))"
        )
        executor = StdioMCPExecutor([sys.executable, "-c", script], timeout_seconds=5)

        with self.assertRaisesRegex(RuntimeError, "no matching"):
            executor("aws-mcp", "list_regions", {})

    def test_managed_aws_proxy_executor_locks_endpoint_and_region_metadata(self):
        executor = ManagedAWSMCPProxyExecutor(
            ["uvx", "mcp-proxy-for-aws-cli@reviewed"],
            resource_region="us-east-2",
        )

        self.assertEqual(
            executor._command,
            (
                "uvx",
                "mcp-proxy-for-aws-cli@reviewed",
                "https://aws-mcp.us-east-1.api.aws/mcp",
                "--metadata",
                "AWS_REGION=us-east-2",
            ),
        )

    def test_managed_aws_proxy_executor_rejects_untrusted_endpoints(self):
        invalid_endpoints = (
            "http://aws-mcp.us-east-1.api.aws/mcp",
            "https://example.com/mcp",
            "https://aws-mcp.us-east-1.api.aws/not-mcp",
            "https://user@aws-mcp.us-east-1.api.aws/mcp",
            "https://aws-mcp.us-east-1.api.aws/mcp?oauth=initialize",
        )

        for endpoint in invalid_endpoints:
            with self.subTest(endpoint=endpoint), self.assertRaises(ValueError):
                ManagedAWSMCPProxyExecutor(["proxy"], endpoint=endpoint)

    def test_managed_aws_proxy_executor_rejects_floating_package_version(self):
        for command in (
            ["uvx", "mcp-proxy-for-aws-cli"],
            ["uvx", "mcp-proxy-for-aws-cli@latest"],
        ):
            with self.subTest(command=command), self.assertRaisesRegex(ValueError, "pinned version"):
                ManagedAWSMCPProxyExecutor(command)


class _HTTPResponse:
    def __init__(self, status, payload, session_id=None):
        self.status = status
        self._raw = b"" if payload is None else json.dumps(payload).encode("utf-8")
        self._session_id = session_id

    def read(self, amount=None):
        return self._raw if amount is None else self._raw[:amount]

    def getheader(self, name, default=None):
        if name.lower() == "mcp-session-id":
            return self._session_id or default
        if name.lower() == "content-type":
            return "application/json"
        return default


class _HTTPSConnection:
    def __init__(self, responses, host, timeout=None):
        self._responses = responses
        self.host = host
        self.timeout = timeout
        self.requests = []

    def request(self, method, path, body=None, headers=None):
        self.requests.append((method, path, body, headers or {}))

    def getresponse(self):
        return self._responses.pop(0)

    def close(self):
        pass


if __name__ == "__main__":
    unittest.main()
