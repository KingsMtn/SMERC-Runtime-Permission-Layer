import json
import subprocess
import sys
import unittest
from pathlib import Path

from reference_engine.mcp_aws_enforcement_adapter import AWSMCPEnforcementAdapter, StdioMCPExecutor, TOOL_NAME


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
                },
            },
        },
    }


class AWSMCPEnforcementAdapterTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
