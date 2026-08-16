import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from reference_engine.mcp_transport_proxy import (
    MCP_TRANSPORT_PROXY_VERSION,
    render_markdown,
    run_mcp_transport_proxy,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
DELETE_ENVELOPE = ROOT / "examples" / "mcp" / "transport_proxy_delete_customer_records.json"
SEARCH_ENVELOPE = ROOT / "examples" / "mcp" / "transport_proxy_search_docs.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class MCPTransportProxyTests(unittest.TestCase):
    def test_enforce_mode_returns_jsonrpc_error_for_blocked_destructive_call(self):
        report = run_mcp_transport_proxy(load(DELETE_ENVELOPE))
        response = report["mcp_jsonrpc_response"]

        self.assertEqual(report["schema"], MCP_TRANSPORT_PROXY_VERSION)
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], "tool-call-001")
        self.assertIn("error", response)
        self.assertEqual(response["error"]["code"], -32070)
        self.assertEqual(response["error"]["data"]["proxy_action"], "block_tool_call")
        self.assertEqual(response["error"]["data"]["posture"], "DENY")
        self.assertEqual(response["error"]["data"]["route_state"], "BLOCK")
        self.assertFalse(report["proxy_report"]["proxy_response"]["should_forward_tool_call"])

    def test_enforce_mode_returns_jsonrpc_result_for_safe_read_call(self):
        report = run_mcp_transport_proxy(load(SEARCH_ENVELOPE))
        response = report["mcp_jsonrpc_response"]

        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], "tool-call-002")
        self.assertIn("result", response)
        self.assertNotIn("error", response)
        self.assertEqual(response["result"]["smerc_proxy"]["proxy_action"], "forward_tool_call")
        self.assertEqual(response["result"]["smerc_proxy"]["posture"], "ALLOW")
        self.assertTrue(report["proxy_report"]["proxy_response"]["should_forward_tool_call"])

    def test_shadow_mode_forwards_but_preserves_block_recommendation(self):
        envelope = load(DELETE_ENVELOPE)
        envelope["mode"] = "shadow"
        report = run_mcp_transport_proxy(envelope)
        response = report["mcp_jsonrpc_response"]

        self.assertIn("result", response)
        self.assertEqual(response["result"]["smerc_proxy"]["mode"], "shadow")
        self.assertEqual(response["result"]["smerc_proxy"]["proxy_action"], "observe_and_forward_tool_call")
        self.assertEqual(report["proxy_report"]["governance_report"]["recommended_mcp_result"], "block_tool_call")

    def test_tool_name_mismatch_is_rejected(self):
        envelope = load(SEARCH_ENVELOPE)
        envelope["mcp_jsonrpc_request"]["params"]["name"] = "different_tool"
        with self.assertRaisesRegex(ValueError, "must match"):
            run_mcp_transport_proxy(envelope)

    def test_unsupported_method_is_rejected(self):
        envelope = load(SEARCH_ENVELOPE)
        envelope["mcp_jsonrpc_request"]["method"] = "resources/read"
        with self.assertRaisesRegex(ValueError, "tools/call"):
            run_mcp_transport_proxy(envelope)

    def test_markdown_and_outputs_are_reviewable(self):
        report = run_mcp_transport_proxy(load(DELETE_ENVELOPE))
        markdown = render_markdown(report)

        self.assertIn("SMERC MCP Transport Proxy Report", markdown)
        self.assertIn("Transport Decision", markdown)
        self.assertIn("block_tool_call", markdown)
        self.assertIn("JSON-RPC Response Shape", markdown)
        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / "transport.json"
            markdown_path = Path(directory) / "transport.md"
            write_outputs(report, json_path=json_path, markdown_path=markdown_path)
            self.assertTrue(json_path.exists())
            self.assertTrue(markdown_path.exists())

    def test_cli_writes_report_files(self):
        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / "transport.json"
            markdown_path = Path(directory) / "transport.md"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "reference_engine.mcp_transport_proxy",
                    "--envelope",
                    str(DELETE_ENVELOPE),
                    "--json-output",
                    str(json_path),
                    "--markdown-output",
                    str(markdown_path),
                    "--pretty",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                timeout=20,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(report["mcp_jsonrpc_response"]["error"]["data"]["proxy_action"], "block_tool_call")
            self.assertIn("SMERC MCP Transport Proxy Report", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
